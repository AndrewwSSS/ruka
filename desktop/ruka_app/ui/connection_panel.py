from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton

from ruka_app.core.protocol import DEFAULT_BAUD_RATE
from ruka_app.core.serial_link import PortInfo

COMMON_BAUD_RATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]


class ConnectionPanel(QGroupBox):
    """Port selection and connect/disconnect controls.

    This widget only emits requests; MainWindow owns the SerialLink and
    drives this panel's visual state back via set_connected/set_disconnected
    once the link confirms what actually happened.
    """

    connect_requested = Signal(str, int)  # device, baud
    disconnect_requested = Signal()
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Connection", parent)

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(240)

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(str(b) for b in COMMON_BAUD_RATES)
        self.baud_combo.setCurrentText(str(DEFAULT_BAUD_RATE))

        self.refresh_button = QPushButton("Refresh")
        self.connect_button = QPushButton("Connect")

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #999;")
        self.status_label = QLabel("Disconnected")

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_combo, 1)
        layout.addWidget(self.refresh_button)
        layout.addWidget(QLabel("Baud:"))
        layout.addWidget(self.baud_combo)
        layout.addWidget(self.connect_button)
        layout.addSpacing(12)
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        self._connected = False

        self.refresh_button.clicked.connect(self.refresh_requested)
        self.connect_button.clicked.connect(self._on_connect_clicked)

    def _on_connect_clicked(self) -> None:
        if self._connected:
            self.disconnect_requested.emit()
            return

        device = self.port_combo.currentData()
        if not device:
            return
        self.connect_requested.emit(device, int(self.baud_combo.currentText()))

    def set_ports(self, ports: list[PortInfo]) -> None:
        current = self.port_combo.currentData()
        self.port_combo.clear()
        for port in ports:
            self.port_combo.addItem(str(port), port.device)
        if current:
            idx = self.port_combo.findData(current)
            if idx >= 0:
                self.port_combo.setCurrentIndex(idx)

    def set_connecting(self) -> None:
        self.connect_button.setEnabled(False)
        self.status_dot.setStyleSheet("color: #d9a400;")
        self.status_label.setText("Connecting…")

    def set_connected(self, port: str) -> None:
        self._connected = True
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Disconnect")
        self.port_combo.setEnabled(False)
        self.baud_combo.setEnabled(False)
        self.status_dot.setStyleSheet("color: #2e7d32;")
        self.status_label.setText(f"Connected — {port}")

    def set_disconnected(self, reason: str = "") -> None:
        self._connected = False
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connect")
        self.port_combo.setEnabled(True)
        self.baud_combo.setEnabled(True)
        self.status_dot.setStyleSheet("color: #999;")
        self.status_label.setText(f"Disconnected — {reason}" if reason else "Disconnected")
