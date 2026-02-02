````markdown
# sysfix-ai

**Safe, modular Linux diagnostics tool with AI-assisted fixes and interactive user control**

---

## Overview

sysfix-ai is designed to detect common Linux system issues—like high memory usage, audio problems, storage capacity, overheating hardware, and motherboard/BIOS warnings—and provide safe, guided fixes. 

Using an intuitive CLI, it offers detailed diagnostics and lets you choose how to handle each problem: kill processes, optimize memory, or skip. You can also opt for AI automation to let sysfix-ai handle everything with caution.

---

## Features

- **Comprehensive diagnostics** for audio, memory leaks, storage, CPU/GPU temperature, and hardware status  
- **Interactive fixes**: Prompted actions like kill (`k`), optimize (`o`), skip (`s`), or automate (`a`)  
- **AI-assisted automation** option for hands-free, careful repairs  
- **Critical BIOS/motherboard warnings** with strong safety alerts — automatic BIOS fixes are disabled by default  
- Modular and extensible architecture for easy expansion

---

## Installation

```bash
git clone https://github.com/useofscript/sysfix-ai.git
cd sysfix-ai
pip install -r requirements.txt
````

---

## Usage

### Run diagnostics

```bash
python -m sysfixai.cli check
```

### Apply fixes interactively

```bash
python -m sysfixai.cli fix <issue_number>
```

Follow on-screen prompts:

* `k`: Kill the problematic process
* `o`: Optimize memory usage
* `s`: Skip this process
* `a`: Automate fixing remaining issues

---

## Important Safety Notes

* **BIOS and motherboard checks show warnings only.**
* Automatic BIOS flashing or modification is **disabled** due to high risk of bricking your device.
* Always backup important data before applying system-level fixes.

---

## Contributing

Pull requests and issues welcome! Please follow coding standards and write tests.

---

## License

MIT License — see [LICENSE](LICENSE)
