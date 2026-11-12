from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout


class LogConsole(QGroupBox):
    """Read-only, timestamped log of everything sent/received on the link."""

    MAX_BLOCKS = 2000

    def __init__(self, parent=None):
        super().__init__("Log", parent)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setMaximumBlockCount(self.MAX_BLOCKS)
        self.text.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = self.text.font()
        font.setFamily("Consolas")
        self.text.setFont(font)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.text.clear)

        top = QHBoxLayout()
        top.addStretch(1)
        top.addWidget(clear_button)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.text)

    def append(self, text: str, prefix: str = "") -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text.appendPlainText(f"[{timestamp}] {prefix}{text}")
