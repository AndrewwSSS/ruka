from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from ruka_app.core import protocol
from ruka_app.core.serial_link import SerialLink
from ruka_app.ui.connection_panel import ConnectionPanel
from ruka_app.ui.log_console import LogConsole
from ruka_app.ui.sequence_panel import SequencePanel
from ruka_app.ui.servo_panel import ServoPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ruka Control")
        self.resize(1150, 700)

        self.link = SerialLink(self)
        self.link.connected.connect(self._on_connected)
        self.link.connection_failed.connect(self._on_connection_failed)
        self.link.disconnected.connect(self._on_disconnected)
        self.link.line_received.connect(self._on_line_received)

        self.connection_panel = ConnectionPanel()
        self.servo_panel = ServoPanel()
        self.sequence_panel = SequencePanel()
        self.log_console = LogConsole()

        central = QWidget()
        outer_layout = QVBoxLayout(central)
        outer_layout.addWidget(self.connection_panel)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.servo_panel)

        right_column = QVBoxLayout()
        right_column.addWidget(self.sequence_panel)
        right_column.addWidget(self.log_console, 1)
        content_layout.addLayout(right_column, 1)

        outer_layout.addLayout(content_layout, 1)
        self.setCentralWidget(central)

        self.connection_panel.refresh_requested.connect(self._refresh_ports)
        self.connection_panel.connect_requested.connect(self._connect)
        self.connection_panel.disconnect_requested.connect(self._disconnect)

        self.servo_panel.angle_changed.connect(self._on_angle_changed)
        self.servo_panel.setEnabled(False)

        self.sequence_panel.save_requested.connect(lambda: self._send(protocol.save_step()))
        self.sequence_panel.run_requested.connect(lambda: self._send(protocol.run_sequence()))
        self.sequence_panel.pause_requested.connect(lambda: self._send(protocol.pause_sequence()))
        self.sequence_panel.reset_requested.connect(lambda: self._send(protocol.reset_sequence()))
        self.sequence_panel.default_requested.connect(self._on_default_requested)
        self.sequence_panel.setEnabled(False)

        self._refresh_ports()

    # -- connection lifecycle -------------------------------------------

    def _refresh_ports(self) -> None:
        self.connection_panel.set_ports(SerialLink.available_ports())

    def _connect(self, port: str, baud: int) -> None:
        self.connection_panel.set_connecting()
        self.log_console.append(f"Connecting to {port} @ {baud}...")
        self.link.open(port, baud)

    def _disconnect(self) -> None:
        self.link.close()

    def _on_connected(self, port: str) -> None:
        self.connection_panel.set_connected(port)
        self.servo_panel.setEnabled(True)
        self.sequence_panel.setEnabled(True)
        self.sequence_panel.reset_local_state()
        self.log_console.append(f"Connected to {port}.")

    def _on_connection_failed(self, message: str) -> None:
        self.connection_panel.set_disconnected("connection failed")
        self.servo_panel.setEnabled(False)
        self.sequence_panel.setEnabled(False)
        self.log_console.append(f"Connection failed: {message}", prefix="! ")
        QMessageBox.warning(self, "Connection failed", message)

    def _on_disconnected(self) -> None:
        self.connection_panel.set_disconnected()
        self.servo_panel.setEnabled(False)
        self.sequence_panel.setEnabled(False)
        self.log_console.append("Disconnected.")

    # -- commands ---------------------------------------------------------

    def _send(self, command: str) -> None:
        if not self.link.is_open:
            self.log_console.append("Not connected — command dropped.", prefix="! ")
            return
        self.link.send(command)
        self.log_console.append(command, prefix="> ")

    def _on_angle_changed(self, index: int, angle: int) -> None:
        self._send(protocol.move_servo(index, angle))

    def _on_default_requested(self) -> None:
        self.servo_panel.set_default_angles_silent()
        self._send(protocol.go_default())

    def _on_line_received(self, line: str) -> None:
        self.log_console.append(line, prefix="< ")
        self.sequence_panel.handle_status_line(line)

    def closeEvent(self, event) -> None:
        self.link.close()
        event.accept()
