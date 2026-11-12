# Ruka Control — `make run` launches the app, `make build` packages it.
# Both bootstrap .venv and install requirements on first use, the same way
# build.sh does, so a fresh clone needs nothing but Python and make.

VENV := .venv
DEPS_STAMP := $(VENV)/.deps-installed
BUILD_STAMP := $(VENV)/.pyinstaller-installed

BOOTSTRAP_PY := $(shell command -v python3 2>/dev/null || command -v py 2>/dev/null || echo python)

# Expanded lazily (`=`, not `:=`): which layout the venv uses — Scripts/ on
# Windows, bin/ elsewhere — is only knowable after $(DEPS_STAMP) has created it.
VENV_PY = $(if $(wildcard $(VENV)/Scripts/python.exe),$(VENV)/Scripts/python.exe,$(VENV)/bin/python)

.DEFAULT_GOAL := help
.PHONY: help run build test deps clean distclean

help:
	@echo "Targets:"
	@echo "  make run        launch the app (python run.py inside .venv)"
	@echo "  make build      package a standalone executable into dist/"
	@echo "  make test       run the unit tests (standard library only)"
	@echo "  make deps       create .venv and install requirements only"
	@echo "  make clean      remove build/ and dist/ and __pycache__ dirs"
	@echo "  make distclean  clean, and remove .venv too"

run: $(DEPS_STAMP)
	$(VENV_PY) run.py

build: $(BUILD_STAMP)
	$(VENV_PY) -m PyInstaller ruka.spec --noconfirm
	@echo "Build complete: dist/Ruka.exe (Windows) or dist/Ruka (macOS/Linux)"

test:
	$(BOOTSTRAP_PY) -m unittest discover -s tests -v

deps: $(DEPS_STAMP)

$(DEPS_STAMP): requirements.txt
	@test -d $(VENV) || $(BOOTSTRAP_PY) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -r requirements.txt
	@touch $@

$(BUILD_STAMP): $(DEPS_STAMP)
	$(VENV_PY) -m pip install pyinstaller
	@touch $@

clean:
	rm -rf build dist
	find . -path ./$(VENV) -prune -o -type d -name __pycache__ -print0 | xargs -0 rm -rf

distclean: clean
	rm -rf $(VENV)
