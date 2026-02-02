import psutil
import shutil
import subprocess
import pulsectl

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
        print("Restarting PulseAudio...")
        subprocess.run(["pulseaudio", "-k"], check=False)
        subprocess.run(["pulseaudio", "--start"], check=False)
    elif is_pipewire_running():
        print("Restarting PipeWire...")
        subprocess.run(["systemctl", "--user", "restart", "pipewire"], check=False)
        subprocess.run(["systemctl", "--user", "restart", "pipewire-pulse"], check=False)
    else:
        print("No recognized audio service running.")

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
        # If PulseAudio check fails, try detecting PipeWire instead
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

    if not issues:
        issues.append("No issues detected.")

    return issues

def apply_fix(issue):
    print(f"Processing fix for: {issue}")

    if "disk space" in issue:
        print("Clearing apt cache and thumbnail cache to free disk space.")
        subprocess.run(["sudo", "apt-get", "clean"], check=False)
        subprocess.run(["rm", "-rf", "~/.cache/thumbnails/*"], shell=True, check=False)

    elif "CPU usage" in issue:
        print("Suggestion: Please check running processes manually.")

    elif "Low available memory" in issue:
        print("Dropping system caches to free memory.")
        subprocess.run(["sudo", "sync"], check=True)
        subprocess.run(["sudo", "bash", "-c", "echo 3 > /proc/sys/vm/drop_caches"], shell=True, check=True)

    elif "swap" in issue:
        print("Swap usage high. Suggest reducing memory usage or adding RAM.")

    elif "Audio system issue" in issue:
        restart_audio_services()

    elif "memory usage by processes" in issue:
        print("Consider closing high-memory applications.")

    else:
        print("No automatic fix available.")
