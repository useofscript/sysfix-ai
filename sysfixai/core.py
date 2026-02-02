import psutil
import shutil
import subprocess
import pulsectl
import click
import gc
import re
import sys

# Global AI automate flag, controls whether to auto-accept prompts
AI_AUTOMATE = False

def prompt_choice(prompt, choices, default='n'):
    """Prompt user with choices, support AI automation."""
    global AI_AUTOMATE
    if AI_AUTOMATE:
        click.echo(f"{prompt} [automated: default '{default}']")
        return default
    choice = ''
    choices_str = '/'.join(choices)
    while choice.lower() not in choices:
        choice = click.prompt(f"{prompt} [{choices_str}]", default=default)
    return choice.lower()

def is_pulseaudio_running():
    try:
        output = subprocess.check_output(["pgrep", "pulseaudio"])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def is_pipewire_running():
    try:
        output = subprocess.check_output(["pgrep", "pipewire"])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def restart_audio_services():
    if is_pulseaudio_running():
        click.echo("Restarting PulseAudio...")
        subprocess.run(["pulseaudio", "-k"], check=False)
        subprocess.run(["pulseaudio", "--start"], check=False)
    elif is_pipewire_running():
        click.echo("Restarting PipeWire...")
        subprocess.run(["systemctl", "--user", "restart", "pipewire"], check=False)
        subprocess.run(["systemctl", "--user", "restart", "pipewire-pulse"], check=False)
    else:
        click.echo("No recognized audio service running.")

def get_bios_info():
    try:
        output = subprocess.check_output(['sudo', 'dmidecode', '-t', 'bios'], text=True)
        return output
    except Exception:
        return None

def diagnose():
    issues = []

    # Disk usage checks (root and /home)
    for partition in ["/", "/home"]:
        try:
            usage = shutil.disk_usage(partition)
            free_gb = usage.free / (1024**3)
            if free_gb < 5:
                issues.append(f"Low disk space: only {free_gb:.2f} GB free on {partition}.")
        except FileNotFoundError:
            continue

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 85:
        issues.append(f"High CPU usage detected: {cpu_percent}%.")

    # Memory usage
    mem = psutil.virtual_memory()
    free_mem_gb = mem.available / (1024**3)
    if free_mem_gb < 1:
        issues.append(f"Low available memory: {free_mem_gb:.2f} GB left.")

    # Swap usage
    swap = psutil.swap_memory()
    if swap.percent > 50:
        issues.append(f"High swap usage: {swap.percent}% used.")

    # Audio check for PulseAudio or PipeWire
    audio_issue = False
    try:
        with pulsectl.Pulse('sysfix-ai') as pulse:
            sinks = pulse.sink_list()
            if not sinks:
                audio_issue = True
            else:
                active_sinks = [s for s in sinks if s.state == pulsectl.PulseSinkState.RUNNING]
                if not active_sinks:
                    audio_issue = True
    except Exception:
        if not (is_pulseaudio_running() or is_pipewire_running()):
            audio_issue = True

    if audio_issue:
        issues.append("Audio system issue detected (no active audio devices or service not running).")

    # Memory hogging processes (>500MB resident memory)
    hogs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            rss_mb = proc.info['memory_info'].rss / (1024**2)
            if rss_mb > 500:
                hogs.append(f"{proc.info['name']} (PID {proc.info['pid']}) using {rss_mb:.1f} MB RAM")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if hogs:
        issues.append(f"High memory usage by processes: {', '.join(hogs[:3])}" + ("..." if len(hogs) > 3 else ""))

    # Hardware temps
    temps = psutil.sensors_temperatures()
    for sensor_name, entries in temps.items():
        for entry in entries:
            if entry.current is not None and entry.current > 85:
                issues.append(f"High temperature alert: {sensor_name} sensor '{entry.label or 'unknown'}' at {entry.current}°C.")

    # Fans
    fans = psutil.sensors_fans()
    if fans:
        for fan_name, entries in fans.items():
            for entry in entries:
                if entry.current == 0:
                    issues.append(f"Fan '{fan_name}' might not be spinning (speed=0).")

    # BIOS info with warnings
    bios_info = get_bios_info()
    if bios_info:
        issues.append(click.style(
            "WARNING: BIOS info detected. DO NOT attempt automated BIOS updates or changes.",
            fg="red", bold=True
        ))
        issues.append(click.style(
            "BIOS flashing is dangerous and can brick your computer if done incorrectly.",
            fg="yellow", bold=True
        ))
    else:
        issues.append("Unable to retrieve BIOS info (dmidecode might require sudo).")

    if not issues:
        issues.append("No issues detected.")

    return issues

def handle_memory_hogs():
    hogs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            rss_mb = proc.info['memory_info'].rss / (1024**2)
            if rss_mb > 500:
                hogs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    for proc in hogs:
        name = proc.info['name']
        pid = proc.info['pid']
        rss_mb = proc.info['memory_info'].rss / (1024**2)
        click.secho(f"Process '{name}' (PID {pid}) is using {rss_mb:.1f} MB RAM.", fg='red')
        choice = prompt_choice("Kill (k), Optimize (o), or Skip (s)?", ['k', 'o', 's'], default='s')
        if choice == 'k':
            try:
                proc.terminate()
                click.echo(f"Terminated process {name} (PID {pid}).")
            except Exception as e:
                click.echo(f"Failed to terminate: {e}")
        elif choice == 'o':
            click.echo(f"Optimizing memory for {name} (PID {pid})...")
            gc.collect()
            subprocess.run(["sudo", "sync"], check=False)
            subprocess.run('sudo bash -c "echo 3 > /proc/sys/vm/drop_caches"', shell=True, check=False)
        else:
            click.echo(f"Skipped {name} (PID {pid}).")

def apply_fix(issue):
    global AI_AUTOMATE
    click.echo(f"Processing fix for: {issue}")

    # Check if user wants AI automation for all remaining fixes
    if not AI_AUTOMATE:
        choice = prompt_choice("Type 'a' to automate all fixes from now on, or press Enter to continue manually", ['a', ''], default='')
        if choice == 'a':
            AI_AUTOMATE = True

    if "disk space" in issue:
        match = re.search(r"only ([\d\.]+) GB free on (.+)\.", issue)
        if match:
            free_gb = float(match.group(1))
            partition = match.group(2)
            click.echo(f"Partition '{partition}' has low free space: {free_gb:.2f} GB.")
            choice = prompt_choice(
                "Clean apt cache (a), clear thumbnail cache (t), show cleanup suggestions (s), or skip (k)?",
                ['a', 't', 's', 'k'],
                default='k'
            )
            if choice == 'a':
                click.echo("Cleaning apt cache...")
                subprocess.run(["sudo", "apt-get", "clean"], check=False)
            elif choice == 't':
                click.echo("Clearing thumbnail cache...")
                subprocess.run(["rm", "-rf", "~/.cache/thumbnails/*"], shell=True, check=False)
            elif choice == 's':
                click.echo(
                    "Suggestions:\n"
                    "- Remove old kernels: sudo apt-get autoremove --purge\n"
                    "- Clear journal logs: sudo journalctl --vacuum-time=2d\n"
                    "- Check large files: sudo du -h / | sort -rh | head -20"
                )
            else:
                click.echo("Skipped storage cleanup.")
        else:
            click.echo("Could not parse disk space issue details.")

    elif "CPU usage" in issue:
        click.echo("Suggestion: Please check running processes manually.")

    elif "Low available memory" in issue:
        click.echo("Dropping system caches to free memory.")
        subprocess.run(["sudo", "sync"], check=False)
        subprocess.run('sudo bash -c "echo 3 > /proc/sys/vm/drop_caches"', shell=True, check=False)

    elif "swap" in issue:
        click.echo("Swap usage high. Suggest reducing memory usage or adding RAM.")

    elif "Audio system issue" in issue:
        restart_audio_services()

    elif "memory usage by processes" in issue:
        handle_memory_hogs()

    elif "temperature alert" in issue.lower() or "fan" in issue.lower():
        click.secho(f"Hardware alert: {issue}", fg='red')
        click.echo("Please manually inspect hardware cooling systems.")
    
    elif "bios" in issue.lower():
        click.secho(f"IMPORTANT: {issue}", fg='red' if "dangerous" in issue.lower() else 'yellow', bold=True)
        click.echo("No automatic BIOS fixes will be attempted.")

    else:
        click.echo("No automatic fix available.")

    click.echo("Fix applied (simulated).")
