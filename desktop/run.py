"""Entry point for running the app directly (`python run.py`) and the
PyInstaller build target (see ruka.spec)."""

from ruka_app.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
