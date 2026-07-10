from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QSlider, QSpinBox, QVBoxLayout, QWidget

from ruka_app.core.paths import resource_path
from ruka_app.core.protocol import MAX_ANGLE, MIN_ANGLE, SERVO_COUNT, SERVO_DEFAULTS

# Fraction of the arm image's height at which each servo's leader line goes
# horizontal, indexed 0-5 (Servo 1..6) -- this is where the line visually
# continues into the slider row, which is not always the same height as the
# joint dot itself (some lines bend up or down before leveling off).
# Measured against resources/arm_image.jpg (537px tall): servo 1 is the
# base-rotation joint at the bottom, servo 6 is the gripper at the top --
# numbering runs bottom-to-top up the kinematic chain.
JOINT_Y_FRACTIONS = [448 / 537, 390 / 537, 250 / 537, 200 / 537, 150 / 537, 98 / 537]

ARM_IMAGE_PATH = resource_path("resources", "arm_image.jpg")

assert len(JOINT_Y_FRACTIONS) == SERVO_COUNT


class _ServoRow(QWidget):
    """One servo's label + slider + spinbox, positioned by _ArmDiagram to
    line up with its joint on the arm image."""

    def __init__(self, index: int, on_change, parent=None):
        super().__init__(parent)
        self.index = index
        self._on_change = on_change
        self._updating = False

        default_angle = SERVO_DEFAULTS[index]

        self.label = QLabel(f"Servo {index + 1}")
        self.label.setFixedWidth(52)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(MIN_ANGLE, MAX_ANGLE)
        self.slider.setValue(default_angle)
        self.slider.setMinimumWidth(140)

        self.spinbox = QSpinBox()
        self.spinbox.setRange(MIN_ANGLE, MAX_ANGLE)
        self.spinbox.setValue(default_angle)
        self.spinbox.setSuffix("°")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)
        self.adjustSize()

    def _on_slider_changed(self, value: int) -> None:
        if self._updating:
            return
        self._updating = True
        self.spinbox.setValue(value)
        self._updating = False
        self._on_change(self.index, value)

    def _on_spinbox_changed(self, value: int) -> None:
        if self._updating:
            return
        self._updating = True
        self.slider.setValue(value)
        self._updating = False
        self._on_change(self.index, value)

    def set_angle_silent(self, angle: int) -> None:
        self._updating = True
        self.slider.setValue(angle)
        self.spinbox.setValue(angle)
        self._updating = False


class _ArmDiagram(QWidget):
    """The arm image on the left with each servo's controls placed, via
    absolute positioning, next to its joint in the image."""

    ROW_GAP_PX = 16

    def __init__(self, rows: list[_ServoRow], parent=None):
        super().__init__(parent)
        self._rows = rows

        self._pixmap = QPixmap(str(ARM_IMAGE_PATH))
        self.image_label = QLabel(self)
        if self._pixmap.isNull():
            self.image_label.setText(f"Missing image:\n{ARM_IMAGE_PATH}")
            self.image_label.setFixedSize(200, 400)
        else:
            self.image_label.setPixmap(self._pixmap)
            self.image_label.setFixedSize(self._pixmap.size())
        self.image_label.move(0, 0)

        row_width = max((row.sizeHint().width() for row in rows), default=260)
        for row in rows:
            row.setParent(self)
            row.resize(row_width, row.sizeHint().height())

        image_size = self.image_label.size()
        self.setMinimumSize(
            image_size.width() + self.ROW_GAP_PX + row_width,
            image_size.height(),
        )
        self._reposition()

    def _reposition(self) -> None:
        image_h = self.image_label.height()
        x = self.image_label.width() + self.ROW_GAP_PX
        for row, fraction in zip(self._rows, JOINT_Y_FRACTIONS):
            y = int(fraction * image_h - row.height() / 2)
            y = max(0, min(y, image_h - row.height()))
            row.move(x, y)


class ServoPanel(QGroupBox):
    """Six servo sliders laid out against a diagram of the arm.

    angle_changed fires at most once per SEND_INTERVAL_MS per servo: dragging
    a slider queues its latest value and a timer flushes the queue, so the
    serial link (9600 baud) only ever sees the newest position instead of
    every intermediate tick.
    """

    angle_changed = Signal(int, int)  # servo_index, angle

    SEND_INTERVAL_MS = 40

    def __init__(self, parent=None):
        super().__init__("Servos", parent)

        self._pending: dict[int, int] = {}
        self.rows = [_ServoRow(i, self._queue_change) for i in range(SERVO_COUNT)]
        self.diagram = _ArmDiagram(self.rows)

        layout = QVBoxLayout(self)
        layout.addWidget(self.diagram)

        self._send_timer = QTimer(self)
        self._send_timer.setInterval(self.SEND_INTERVAL_MS)
        self._send_timer.timeout.connect(self._flush_pending)
        self._send_timer.start()

    def _queue_change(self, index: int, angle: int) -> None:
        self._pending[index] = angle

    def _flush_pending(self) -> None:
        if not self._pending:
            return
        pending, self._pending = self._pending, {}
        for index, angle in pending.items():
            self.angle_changed.emit(index, angle)

    def set_default_angles_silent(self) -> None:
        for row in self.rows:
            row.set_angle_silent(SERVO_DEFAULTS[row.index])
        self._pending.clear()
