#!/usr/bin/env bash
# Builds a standalone app at dist/Ruka.exe (Windows) or dist/Ruka (macOS/Linux).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$root"

if [ ! -d ".venv" ]; then
    if command -v py >/dev/null 2>&1; then
        py -m venv .venv
    else
        python3 -m venv .venv
    fi
fi

if [ -f ".venv/Scripts/python.exe" ]; then
    venv_python=".venv/Scripts/python.exe"
else
    venv_python=".venv/bin/python"
fi

"$venv_python" -m pip install --upgrade pip
"$venv_python" -m pip install -r requirements.txt
"$venv_python" -m pip install pyinstaller

"$venv_python" -m PyInstaller ruka.spec --noconfirm

echo "Build complete: dist/Ruka.exe (Windows) or dist/Ruka (macOS/Linux)"
