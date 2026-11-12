from __future__ import annotations

import re

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QMessageBox, QPushButton

from ruka_app.core.protocol import MAX_STEPS

_SAVED_STEP_RE = re.compile(r"Saved step (\d+)")
_PLAYING_STEP_RE = re.compile(r"Playing step (\d+)/(\d+)")


class SequencePanel(QGroupBox):
    """Save/Run/Pause/Default/Reset controls for the firmware's built-in
    pose-sequence recorder.

    The firmware has no query command, so the step count and playback status
    shown here are inferred: optimistically on every button press, and
    corrected from status lines when they arrive. Status lines only arrive
    over a USB connection -- over Bluetooth this panel is optimistic only.
    """

    save_requested = Signal()
    run_requested = Signal()
    pause_requested = Signal()
    default_requested = Signal()
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Sequence", parent)

        self.save_button = QPushButton("Save Step")
        self.run_button = QPushButton("Run")
        self.pause_button = QPushButton("Pause")
        self.default_button = QPushButton("Move to Default")
        self.reset_button = QPushButton("Reset Sequence")

        self.steps_label = QLabel()
        self.playback_label = QLabel("Idle")

        layout = QGridLayout(self)
        layout.addWidget(self.save_button, 0, 0)
        layout.addWidget(self.run_button, 0, 1)
        layout.addWidget(self.pause_button, 0, 2)
        layout.addWidget(self.default_button, 1, 0)
        layout.addWidget(self.reset_button, 1, 1, 1, 2)
        layout.addWidget(self.steps_label, 2, 0, 1, 3)
        layout.addWidget(self.playback_label, 3, 0, 1, 3)

        self._step_count = 0
        self._refresh_steps_label()

        self.save_button.clicked.connect(self._on_save)
        self.run_button.clicked.connect(self.run_requested)
        self.pause_button.clicked.connect(self.pause_requested)
        self.default_button.clicked.connect(self.default_requested)
        self.reset_button.clicked.connect(self._on_reset)

    def _on_save(self) -> None:
        if self._step_count >= MAX_STEPS:
            return
        self._step_count += 1
        self._refresh_steps_label()
        self.save_requested.emit()

    def _on_reset(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset sequence",
            "Clear all saved steps on the arm? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._step_count = 0
            self._refresh_steps_label()
            self.playback_label.setText("Idle")
            self.reset_requested.emit()

    def _refresh_steps_label(self) -> None:
        self.steps_label.setText(f"Steps saved: {self._step_count} / {MAX_STEPS}")

    def handle_status_line(self, line: str) -> None:
        """Reconcile local state against a status line echoed over USB serial."""
        saved_match = _SAVED_STEP_RE.search(line)
        playing_match = _PLAYING_STEP_RE.search(line)

        if saved_match:
            self._step_count = int(saved_match.group(1))
            self._refresh_steps_label()
        elif playing_match:
            self.playback_label.setText(f"Playing step {playing_match.group(1)}/{playing_match.group(2)}")
        elif line == "Playback finished.":
            self.playback_label.setText("Idle")
        elif line == "Reset.":
            self._step_count = 0
            self._refresh_steps_label()
            self.playback_label.setText("Idle")

    def reset_local_state(self) -> None:
        self._step_count = 0
        self._refresh_steps_label()
        self.playback_label.setText("Idle")
