# sysfix-ai

A safe, modular Linux diagnostics tool that detects common system issues and applies controlled, low-risk fixes with optional AI assistance.

## Overview

sysfix-ai is an open-source project focused on **diagnosis first, automation second**.  
It collects structured system data, identifies common failure modes, and explains likely root causes before suggesting or applying vetted fixes.

All remediation actions are explicitly whitelisted, risk-scored, and auditable.  
Arbitrary command execution is intentionally not supported.

## Goals

- Diagnose common Linux system issues
- Explain problems clearly and transparently
- Apply low-risk, controlled fixes
- Keep a human in the loop by default
- Avoid unsafe “one-click optimizer” behavior

## Non-Goals

- Kernel replacement
- Firmware or BIOS flashing
- Bootloader modification
- Blind system “tuning” or optimization

## Supported Systems

- Fedora (primary target)
- Other systemd-based distributions (planned)

## Architecture (High Level)

- System data collection (logs, disk, services, network, audio)
- Rule-based diagnostics
- Optional AI-assisted analysis
- Whitelisted remediation actions
- Post-fix verification

## Project Status

Early development.  
Initial focus is on read-only diagnostics and safe, low-risk fixes.

## License

MIT
