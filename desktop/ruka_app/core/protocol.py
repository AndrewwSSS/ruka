"""Serial command protocol of the Ruka firmware (firmware/src/main.cpp).

Commands are plain text terminated with ';'. Status lines come back over USB
only; a Bluetooth session is send-only. See docs/protocol.md.
"""

SERVO_COUNT = 6
MIN_ANGLE = 0
MAX_ANGLE = 180
SERVO_DEFAULTS = [90, 100, 100, 90, 70, 90]  # must match SERVO_DEFAULTS in firmware/src/main.cpp
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
