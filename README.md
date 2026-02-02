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



## Requirements

**Operating System:** Linux (tested on Fedora, Ubuntu, Debian)

**Python:** 3.8 or newer

**Python dependencies:**
- psutil
- click

Install with:
```bash
pip install psutil click
```

**Ollama:** Required for local AI-powered fixes
- Download and install from: https://ollama.com/download
- Start the Ollama server: `ollama serve`


**Required Ollama model:** lfm2.5-thinking

You must download the model from the official Ollama model registry:

1. Make sure Ollama is installed and running (`ollama serve`).
2. Pull the model using this command:
	```bash
	ollama pull lfm2.5-thinking
	```
	This will download the model from Ollama's official servers to your local machine.
3. The model will be stored in your Ollama models directory (usually `~/.ollama/models`).

For more details, see: https://ollama.com/library/lfm2.5-thinking

**Note:** No external servers or cloud services are used. All AI features run locally via Ollama.

---

## Installation

```bash
git clone https://github.com/useofscript/sysfix-ai.git
cd sysfix-ai
# Install Python dependencies
pip install psutil click
# Install Ollama and pull the lfm2.5-thinking model (see above)
```

---

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
