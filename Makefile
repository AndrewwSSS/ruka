# Common tasks for the firmware and the desktop app. `make` lists them.

PIO ?= $(shell command -v pio 2>/dev/null || echo $(HOME)/.platformio/penv/bin/pio)
FIRMWARE := firmware
DESKTOP := desktop

.DEFAULT_GOAL := help
.PHONY: help firmware upload monitor app app-build test check clean

help:
	@echo "Firmware:"
	@echo "  make firmware   build the sketch for the Uno"
	@echo "  make upload     build and upload it to the connected board"
	@echo "  make monitor    open the serial monitor (9600 baud)"
	@echo "Desktop app:"
	@echo "  make app        run the app from source"
	@echo "  make app-build  package a standalone executable into desktop/dist/"
	@echo "Both:"
	@echo "  make test       run the desktop app's unit tests"
	@echo "  make check      unit tests plus the firmware build, as CI runs them"
	@echo "  make clean      remove firmware and app build output"

firmware:
	cd $(FIRMWARE) && "$(PIO)" run -e uno

upload:
	cd $(FIRMWARE) && "$(PIO)" run -e uno -t upload

monitor:
	cd $(FIRMWARE) && "$(PIO)" device monitor -e uno

app:
	$(MAKE) -C $(DESKTOP) run

app-build:
	$(MAKE) -C $(DESKTOP) build

test:
	$(MAKE) -C $(DESKTOP) test

check: test firmware

clean:
	cd $(FIRMWARE) && "$(PIO)" run -e uno -t clean
	$(MAKE) -C $(DESKTOP) clean
