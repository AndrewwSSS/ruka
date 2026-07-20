# Ruka Control

Cross-platform desktop app (Windows / macOS / Linux) for driving the Ruka
robotic arm — a 6-servo arm controlled by an Arduino Uno, connected over USB
serial or a paired HC-05 Bluetooth module. Built with PySide6 + pyserial.

<img width="1145" height="730" alt="image" src="https://github.com/user-attachments/assets/f6660eb1-e9d7-407c-ad2e-2df73e21cdb2" />


## Requirements

- Python3

## Setup

```bash
py -m venv .venv   # or: python3 -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash); use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

## Connecting

- **USB**: plug in the Arduino, pick the port it enumerates as (usually
  `COMx`), baud `9600`, click Connect.
- **Bluetooth**: pair the HC-05 module first via Windows Bluetooth settings
  (default PIN is usually `1234` or `0000`) — that creates an outgoing COM
  port you can select the same way, baud `9600`.

## Packaging a standalone executable

```bash
./build.sh
```

Produces a single portable executable: `dist\Ruka.exe` on Windows,
`dist/Ruka` on macOS/Linux. PyInstaller doesn't cross-compile, so build on each OS separately — `./build.sh` works unchanged on all three.

