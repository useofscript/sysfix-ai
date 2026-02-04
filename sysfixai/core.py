import socket
def is_ollama_running(host='127.0.0.1', port=11434, timeout=1):
    """Check if Ollama server is running locally."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def ai_auto_fix(issues):
    if not is_ollama_running():
        print("[WARNING] Ollama server is not running. Please start it with: ollama serve")
        return
    for issue in issues:
        print(f"AI is fixing: {issue}")
        ai_response = ask_ai_for_fix(issue)
        # Filter out 'thinking out loud' and only show final advice
        advice_lines = [line for line in ai_response.splitlines() if line.strip()]
        final_advice = None
        for line in reversed(advice_lines):
            # Look for lines starting with Recommendation, or bolded, or ending with a period
            if line.strip().lower().startswith("recommendation:") or line.strip().startswith("**Recommendation"):
                final_advice = line.strip().replace("**Recommendation:**", "").replace("Recommendation:", "").strip()
                break
            elif (len(line.strip()) > 10 and not line.lower().startswith("okay") and not line.lower().startswith("wait") and not line.lower().startswith("first")):
                final_advice = line.strip()
                break
        if not final_advice:
            final_advice = advice_lines[-1] if advice_lines else ai_response
        print(f"AI advice: {final_advice}")
        advice = final_advice.lower()
        if "terminate" in advice or "kill" in advice:
            if "chrome" in advice:
                print("[AI ACTION] Terminating chrome processes...")
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        try:
                            p = psutil.Process(proc.info['pid'])
                            p.terminate()
                            p.wait(timeout=3)
                            print(f"Terminated chrome (PID {proc.info['pid']})")
                        except Exception as e:
                            print(f"Failed to terminate chrome: {e}")
            elif "plasmashell" in advice:
                print("[AI ACTION] Terminating plasmashell process...")
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and 'plasmashell' in proc.info['name'].lower():
                        try:
                            p = psutil.Process(proc.info['pid'])
                            p.terminate()
                            p.wait(timeout=3)
                            print(f"Terminated plasmashell (PID {proc.info['pid']})")
                        except Exception as e:
                            print(f"Failed to terminate plasmashell: {e}")
        elif "bios" in advice:
            print("[AI ACTION] BIOS changes are NOT performed automatically for safety reasons.")
            print("AI can only provide advice or resources. Please refer to your motherboard/computer manufacturer's website for BIOS updates and instructions.")
        elif "free up space" in advice or "disk space" in advice or "storage" in advice:
            print("[AI ACTION] Attempting to free up disk space...")
            free_space()
        elif "optimize" in advice:
            print("[AI ACTION] Optimizing memory usage...")
            handle_memory_hogs()
        elif "skip" in advice:
            print("[AI ACTION] Skipping issue as per AI advice.")
        elif "consult" in advice or "technician" in advice or "professional" in advice:
            print("[AI ACTION] AI recommends consulting a technician or professional. No automatic action taken.")
        else:
            print("[AI ACTION] No direct action mapped for AI advice. Please review manually.")
import psutil
import subprocess
import shutil
import os
from sysfixai.ai import ask_ai_for_fix, ask_ai_deep_dive
from termcolor import colored
from termcolor import colored

def diagnose():
    """Run system diagnostics and return list of detected issues."""
    issues = []
    issues.extend(check_audio())
    issues.extend(check_memory())
    issues.extend(check_storage())
    issues.extend(check_temperatures())
    issues.extend(check_bios())
    issues.extend(check_motherboard())
    issues.extend(check_system_info())
    return issues if issues else ["No issues detected."]
def check_motherboard():
    issues = []
    try:
        # Try to get motherboard info using dmidecode
        if shutil.which("dmidecode"):
            result = subprocess.run(["sudo", "dmidecode", "-t", "baseboard"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
                info = []
                for line in lines:
                    if any(key in line.lower() for key in ["manufacturer", "product name", "version", "serial number"]):
                        info.append(line)
                if info:
                    issues.append("Motherboard info: " + ", ".join(info))
                else:
                    issues.append("Motherboard info could not be determined.")
            else:
                issues.append("Failed to retrieve motherboard info (dmidecode error).")
        else:
            issues.append("dmidecode not found. Cannot retrieve motherboard info.")
    except Exception as e:
        issues.append(f"Error checking motherboard info: {e}")
    return issues
def check_system_info():
    issues = []
    try:
        uname = os.uname()
        issues.append(f"System: {uname.sysname} {uname.release} ({uname.machine})")
        issues.append(f"Node: {uname.nodename}")
        # Try to get CPU info
        cpuinfo = None
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.lower().startswith("model name"):
                        cpuinfo = line.strip().split(":", 1)[-1].strip()
                        break
        if cpuinfo:
            issues.append(f"CPU: {cpuinfo}")
        # Try to get RAM info
        try:
            import psutil
            mem = psutil.virtual_memory()
            issues.append(f"RAM: {mem.total // (1024*1024)} MB total")
        except Exception:
            pass
    except Exception as e:
        issues.append(f"Error checking system info: {e}")
    return issues

def check_audio():
    issues = []
    # Check PulseAudio status
    try:
        result = subprocess.run(["pactl", "info"], capture_output=True, text=True)
        if "Server Name" not in result.stdout:
            issues.append("Audio system check failed (PulseAudio may not be running).")
    except Exception:
        issues.append("Audio system check failed (PulseAudio command not found).")
    return issues

def check_memory():
    issues = []
    # Check for high memory usage processes
    hogs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            if mem_mb > 500:  # threshold
                hogs.append((proc.info['name'], proc.info['pid'], mem_mb))
        except Exception:
            continue
    if hogs:
        desc = "High memory usage by processes: " + ", ".join(
            f"{name} (PID {pid}) using {mem:.1f} MB RAM" for name, pid, mem in hogs)
        issues.append(desc)
    return issues

def check_storage():
    issues = []
    total, used, free = shutil.disk_usage("/")
    used_pct = used / total * 100
    if used_pct > 90:
        issues.append(f"Storage almost full: {used_pct:.1f}% used.")
    return issues

def check_temperatures():
    issues = []
    try:
        import psutil._pslinux as pslinux  # may not always be available
        temps = psutil.sensors_temperatures()
        if temps:
            for sensor, entries in temps.items():
                for entry in entries:
                    if entry.current > 85:
                        issues.append(f"High temperature alert: {sensor} sensor '{entry.label or entry.device}' at {entry.current:.1f}°C.")
    except Exception:
        pass
    return issues

def check_bios():
    issues = []
    try:
        # Reading BIOS info with dmidecode requires root, so just warn user
        bios_warning = [
            colored("WARNING: BIOS info detected. DO NOT attempt automated BIOS updates or changes.", "red", attrs=["bold"]),
            colored("BIOS flashing is dangerous and can brick your computer if done incorrectly.", "yellow", attrs=["bold"])
        ]
        # Let's say if dmidecode is installed, show this warning:
        if shutil.which("dmidecode"):
            issues.extend(bios_warning)
    except Exception:
        pass
    return issues

def apply_fix(issue):
    print(f"Applying fix for: {issue}")
    if "memory usage" in issue:
        handle_memory_hogs()
    elif "storage almost full" in issue:
        handle_storage()
    elif "Audio system" in issue:
        print("No automatic fix available for audio issues.")
    elif "temperature alert" in issue:
        print("Temperature is high, please ensure proper cooling manually.")
    elif "BIOS" in issue:
        print(colored("BIOS fixes are not supported automatically due to risk of bricking the system.", "red"))
    else:
        print("No automatic fix available.")
    print("Fix applied (simulated).")

def handle_memory_hogs():
    hogs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            if mem_mb > 500:
                hogs.append((proc.info['name'], proc.info['pid'], mem_mb))
        except Exception:
            continue

    if not hogs:
        print("No high memory usage processes found.")
        return

    for name, pid, mem in hogs:
        while True:
            prompt = f"Process '{name}' (PID {pid}) is using {mem:.1f} MB RAM.\nKill (k), Optimize (o), Skip (s), or AI (auto)?: "
            choice = input(prompt).strip()
            choice_lower = choice.lower()
            if choice_lower == 'k':
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                    p.wait(timeout=3)
                    print(f"Killed process '{name}' (PID {pid}).")
                except Exception as e:
                    print(f"Failed to kill process: {e}")
                break
            elif choice_lower == 'o':
                optimize_process(pid, name)
                break
            elif choice_lower == 's':
                print(f"Skipped {name} (PID {pid}).")
                break
            elif choice_lower == 'ai':
                ai_choice = ask_ai_for_fix(f"Should I kill, optimize, or skip process '{name}' with PID {pid} using {mem:.1f} MB RAM on a Linux system? Answer with one letter: k, o, or s.")
                ai_choice = ai_choice.strip().lower()
                if ai_choice in ('k', 'o', 's'):
                    print(f"AI chose: {ai_choice}")
                    if ai_choice == 'k':
                        try:
                            p = psutil.Process(pid)
                            p.terminate()
                            p.wait(timeout=3)
                            print(f"Killed process '{name}' (PID {pid}) by AI choice.")
                        except Exception as e:
                            print(f"Failed to kill process: {e}")
                    elif ai_choice == 'o':
                        optimize_process(pid, name)
                    else:
                        print(f"Skipped {name} (PID {pid}) by AI choice.")
                    break
                else:
                    print("AI returned invalid choice. Please enter k, o, s, or AI.")
            else:
                print("Invalid input. Please enter k, o, s, or AI.")

def optimize_process(pid, name):
    print(f"Optimizing memory for {name} (PID {pid})...")
    try:
        # This will drop caches to free up memory - requires sudo
        subprocess.run(["sudo", "bash", "-c", "echo 3 > /proc/sys/vm/drop_caches"], check=True)
        print(f"Optimized memory for {name} (PID {pid}).")
    except subprocess.CalledProcessError:
        print("Failed to optimize memory. You may need to run with sudo or adjust permissions.")

def handle_storage():
    total, used, free = shutil.disk_usage("/")
    used_pct = used / total * 100
    print(f"Storage usage at {used_pct:.1f}%")
    while True:
        choice = input("Would you like to try to free up space? (y/n/AI): ").strip()
        choice_lower = choice.lower()
        if choice_lower == 'y':
            free_space()
            break
        elif choice_lower == 'n':
            print("Skipping storage optimization.")
            break
        elif choice_lower == 'ai':
            ai_choice = ask_ai_for_fix("Should I try to free up disk space on the system? Answer yes or no.")
            if ai_choice.strip().lower().startswith('y'):
                free_space()
            else:
                print("Skipping storage optimization by AI decision.")
            break
        else:
            print("Please enter y, n, or AI.")

def free_space():
    print("Attempting to free space by clearing apt cache and systemd journal...")
    try:
        subprocess.run(["sudo", "apt-get", "clean"], check=True)
        subprocess.run(["sudo", "journalctl", "--vacuum-time=2d"], check=True)
        print("Freed up disk space.")
    except subprocess.CalledProcessError:
        print("Failed to free space automatically.")
def ai_deep_dive():
    """Interactive AI troubleshooting mode for complex issues."""
    if not is_ollama_running():
        print("[WARNING] Ollama server is not running. Please start it with: ollama serve")
        return
    
    print("Welcome to Deep Dive mode. I will ask you questions to diagnose complex issues.")
    
    # Step 1: Ask about the main issue
    main_issue = input("What is the main issue you are experiencing? (e.g., slow performance, crashes, network problems): ")
    
    # Step 2: Ask for additional details
    details = input("Please provide any additional details or symptoms: ")
    
    # Step 3: Ask about recent changes
    recent_changes = input("Have you made any recent changes to your system? (e.g., software installations, updates): ")
    
    # Step 4: Combine inputs and query the AI
    combined_prompt = (
        f"User Issue: {main_issue}\n"
        f"Details: {details}\n"
        f"Recent Changes: {recent_changes}\n"
        "Provide a detailed analysis and step-by-step troubleshooting guide."
    )
    
    ai_response = ask_ai_deep_dive(combined_prompt)
    print(f"\nAI Analysis:\n{ai_response}")
    
    # Step 5: Ask if the user wants to apply any fixes
    apply_fix = input("\nDo you want to apply any of the suggested fixes? (y/n): ").strip().lower()
    if apply_fix == 'y':
        print("Applying fixes...")
        # Here you can add logic to apply fixes based on the AI response
        print("Fixes applied (simulated).")
    else:
        print("No fixes applied. You can manually follow the AI's recommendations.")

