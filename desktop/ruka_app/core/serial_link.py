"""Threaded serial connection to the Ruka arm.

Both the USB link and a paired HC-05 Bluetooth link show up to the OS as an
ordinary COM/serial port, so a single SerialLink handles either -- the caller
just picks a port from SerialLink.available_ports().
"""

from __future__ import annotations

import queue
import time
from dataclasses import dataclass

import serial
import serial.tools.list_ports
from PySide6.QtCore import QThread, Signal


@dataclass(frozen=True)
class PortInfo:
    device: str
    description: str

    def __str__(self) -> str:
        return f"{self.device} — {self.description}" if self.description else self.device


class SerialLink(QThread):
    """Owns one pyserial connection on a background thread.

    Incoming bytes are polled continuously and emitted line by line via
    line_received. Outgoing commands are queued from the GUI thread with
    send() and drained here, so a slow or blocked port never stalls the UI.
    """

    connected = Signal(str)
    connection_failed = Signal(str)
    disconnected = Signal()
    line_received = Signal(str)

    POLL_INTERVAL_S = 0.02

    def __init__(self, parent=None):
        super().__init__(parent)
        self._port: str = ""
        self._baud_rate: int = 9600
        self._serial: serial.Serial | None = None
        self._out_queue: "queue.Queue[str]" = queue.Queue()
        self._stop_requested = False

    @staticmethod
    def available_ports() -> list[PortInfo]:
        return [
            PortInfo(p.device, "" if p.description == "n/a" else p.description)
            for p in serial.tools.list_ports.comports()
        ]

    def open(self, port: str, baud_rate: int = 9600) -> None:
        self._port = port
        self._baud_rate = baud_rate
        self._stop_requested = False
        self.start()

    def close(self) -> None:
        if not self.isRunning():
            return
        self._stop_requested = True
        self.wait(2000)

    def send(self, command: str) -> None:
        if self.isRunning():
            self._out_queue.put(command)

    @property
    def is_open(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def run(self) -> None:
        try:
            self._serial = serial.Serial(self._port, self._baud_rate, timeout=0)
        except serial.SerialException as exc:
            self._serial = None
            self.connection_failed.emit(str(exc))
            return

        self.connected.emit(self._port)

        buffer = b""
        try:
            while not self._stop_requested:
                sent = False
                while not self._out_queue.empty():
                    command = self._out_queue.get_nowait()
                    self._serial.write(command.encode("ascii"))
                    sent = True

                waiting = self._serial.in_waiting
                if waiting:
                    buffer += self._serial.read(waiting)
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        text = line.decode("ascii", errors="replace").strip()
                        if text:
                            self.line_received.emit(text)
                elif not sent:
                    time.sleep(self.POLL_INTERVAL_S)
        finally:
            self._serial.close()
            self._serial = None
            self.disconnected.emit()
