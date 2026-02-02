import os
import subprocess
import psutil
import shutil
import click
from sysfixai.ai import query_granite4

def diagnose():
    issues = []

    # Audio check
    if not is_pulseaudio_running():
        issues.append("Audio system check failed (PulseAudio may not be running).")

    # Memory hogs
    memory_hogs = get_high_memory_processes()
    if memory_hogs:
        hogs_str = ", ".join(
            f"{p.name()} (PID {p.pid}) using {p.memory_info().rss / (1024 ** 2):.1f} MB RAM"
            for p in memory_hogs
        )
        issues.append(f"High memory usage by processes: {hogs_str}...")

    # Temperature check
    temps = get_high_temperatures()
    for sensor, temp in temps.items():
        issues.append(f"High temperature alert: {sensor} sensor '{temp['label']}' at {temp['temp']}°C.")

    # Storage check
    storage_issues = get_storage_issues()
    if storage_issues:
        for mount_point, usage_percent in storage_issues.items():
            issues.append(f"High storage usage: {mount_point} at {usage_percent:.1f}% capacity.")

    # BIOS warning (mock check)
    if bios_info_detected():
        issues.append("WARNING: BIOS info detected. DO NOT attempt automated BIOS updates or changes.")
        issues.append("BIOS flashing is dangerous and can brick your computer if done incorrectly.")

    if not issues:
        issues.append("No issues detected.")

    return issues

def is_pulseaudio_running():
    try:
        result = subprocess.run(["pidof", "pulseaudio"], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except Exception:
        return False

def get_high_memory_processes(threshold_mb=500):
    hogs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 ** 2)
            if mem_mb >= threshold_mb:
                hogs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return hogs

def get_high_temperatures(threshold_c=85):
    temps = {}
    try:
        import sensors  # requires 'py-sensors' or similar; fallback if unavailable
        chip_temps = sensors.get_temperatures()
        for chip, entries in chip_temps.items():
            for entry in entries:
                if entry.current >= threshold_c:
                    temps[chip] = {'label': entry.label, 'temp': entry.current}
    except ImportError:
        # Could implement fallback using lm-sensors command or skip
        pass
    except Exception:
        pass
    return temps

def get_storage_issues(threshold_percent=90):
    issues = {}
    partitions = psutil.disk_partitions()
    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            if usage.percent >= threshold_percent:
                issues[part.mountpoint] = usage.percent
        except (PermissionError, FileNotFoundError):
            continue
    return issues

def bios_info_detected():
    # This is a mock, replace with real detection if needed
    bios_path = "/sys/class/dmi/id/bios_version"
    return os.path.exists(bios_path)

def apply_fix(issue):
    print(f"Processing fix for: {issue}")

    if "Audio system check failed" in issue:
        print("No automatic fix available for audio system issues. Please check PulseAudio or PipeWire services.")
        return

    if "High memory usage" in issue:
        handle_memory_hogs()
        return

    if "High temperature alert" in issue:
        print("Warning: High temperature detected. Consider improving cooling or shutting down intensive tasks.")
        return

    if "High storage usage" in issue:
        handle_storage_optimization()
        return

    if "BIOS info detected" in issue:
        print("\033[91mWARNING: BIOS related issues detected. Automatic fixes are disabled to prevent bricking your system.\033[0m")
        return

    # No predefined fix found, use Granite4 AI suggestion:
    print("No predefined fix found. Consulting AI assistant...")
    response = query_granite4(f"How to fix this Linux system issue? {issue}")
    print("\nAI Suggestion:\n" + response)

def handle_memory_hogs():
    hogs = get_high_memory_processes()
    if not hogs:
        print("No high memory usage processes detected.")
        return

    for proc in hogs:
        mem_mb = proc.memory_info().rss / (1024 ** 2)
        action = prompt_user(f"Process '{proc.name()}' (PID {proc.pid}) is using {mem_mb:.1f} MB RAM.\nKill (k), Optimize (o), or Skip (s)? [s]: ", default="s")
        if action == "k":
            try:
                proc.kill()
                print(f"Killed process {proc.name()} (PID {proc.pid}).")
            except Exception as e:
                print(f"Failed to kill process: {e}")
        elif action == "o":
            print(f"Optimizing memory for {proc.name()} (PID {proc.pid})...")
            optimize_process_memory(proc)
        else:
            print(f"Skipped {proc.name()} (PID {proc.pid}).")

def optimize_process_memory(proc):
    try:
        # Drop caches (requires sudo)
        subprocess.run(["sudo", "bash", "-c", "echo 3 > /proc/sys/vm/drop_caches"], check=True)
        # Send SIGUSR1 or similar if app supports memory cleanup
        proc.send_signal(subprocess.signal.SIGUSR1)
        print(f"Memory optimized for {proc.name()} (PID {proc.pid}).")
    except subprocess.CalledProcessError:
        print("Failed to drop caches. Make sure you have sudo permissions.")
    except Exception as e:
        print(f"Failed to optimize memory: {e}")

def handle_storage_optimization():
    issues = get_storage_issues()
    if not issues:
        print("No high storage usage detected.")
        return

    for mount, usage in issues.items():
        action = prompt_user(f"Storage at {mount} is {usage:.1f}% full.\nClean cache/temp files? yes/no [no]: ", default="no")
        if action == "yes":
            try:
                clean_cache(mount)
                print(f"Cache cleaned on {mount}.")
            except Exception as e:
                print(f"Failed to clean cache: {e}")
        else:
            print(f"Skipped cleaning on {mount}.")

def clean_cache(mount_point):
    cache_dirs = [
        os.path.join(mount_point, "var/cache"),
        os.path.expanduser("~/.cache")
    ]
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            subprocess.run(["sudo", "rm", "-rf", cache_dir], check=False)

def prompt_user(prompt, default=""):
    try:
        response = input(prompt).strip().lower()
        if not response and default:
            return default
        return response
    except EOFError:
        return default
