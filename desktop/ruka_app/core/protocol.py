"""Serial command protocol for the Ruka robotic arm firmware.

Mirrors src/main.cpp in the Ruka-main PlatformIO project: every command is a
plain-text line terminated with ';'. There is no query/response API in the
firmware -- status lines it prints (e.g. "Saved step 3") are written to the
hardware USB Serial only. The HC-05 Bluetooth link (SoftwareSerial) can send
commands to the arm but never receives those status lines back, so a
Bluetooth-connected session is send-only from the app's point of view.
"""

SERVO_COUNT = 6
MIN_ANGLE = 0
MAX_ANGLE = 180
SERVO_DEFAULTS = [90, 170, 100, 90, 55, 90]  # matches SERVO_DEFAULTS in main.cpp, indexed by servo 1-6
MAX_STEPS = 50
DEFAULT_BAUD_RATE = 9600
TERMINATOR = ";"

assert len(SERVO_DEFAULTS) == SERVO_COUNT


def move_servo(servo_index: int, angle: int) -> str:
    """servo_index is 0-based (0-5); firmware addresses servos as '1'-'6'."""
    if not 0 <= servo_index < SERVO_COUNT:
        raise ValueError(f"servo_index must be 0-{SERVO_COUNT - 1}, got {servo_index}")
    angle = max(MIN_ANGLE, min(MAX_ANGLE, int(angle)))
    
    return f"s{servo_index + 1}{angle:03d}{TERMINATOR}"


def save_step() -> str:
    return f"SAVE{TERMINATOR}"


def run_sequence() -> str:
    return f"RUN{TERMINATOR}"


def pause_sequence() -> str:
    return f"PAUSE{TERMINATOR}"


def go_default() -> str:
    return f"DEFAULT{TERMINATOR}"


def reset_sequence() -> str:
    return f"RESET{TERMINATOR}"
