import re
import unittest
from pathlib import Path

from ruka_app.core import protocol

FIRMWARE_MAIN = Path(__file__).resolve().parents[2] / "firmware" / "src" / "main.cpp"


class MoveServoTest(unittest.TestCase):
    def test_sends_one_based_servo_and_angle_as_words(self):
        self.assertEqual(protocol.move_servo(0, 120), "s 1 120;")
        self.assertEqual(protocol.move_servo(5, 7), "s 6 7;")

    def test_clamps_the_angle(self):
        self.assertEqual(protocol.move_servo(0, -10), "s 1 0;")
        self.assertEqual(protocol.move_servo(0, 300), "s 1 180;")

    def test_rejects_an_unknown_servo(self):
        with self.assertRaises(ValueError):
            protocol.move_servo(-1, 90)
        with self.assertRaises(ValueError):
            protocol.move_servo(protocol.SERVO_COUNT, 90)


class SequenceCommandsTest(unittest.TestCase):
    def test_commands_end_with_the_terminator(self):
        self.assertEqual(protocol.save_step(), "SAVE;")
        self.assertEqual(protocol.run_sequence(), "RUN;")
        self.assertEqual(protocol.pause_sequence(), "PAUSE;")
        self.assertEqual(protocol.go_default(), "DEFAULT;")
        self.assertEqual(protocol.reset_sequence(), "RESET;")


class FirmwareAgreementTest(unittest.TestCase):
    """The app's constants must match what the firmware was built with."""

    @classmethod
    def setUpClass(cls):
        cls.source = FIRMWARE_MAIN.read_text(encoding="utf-8")

    def define(self, name):
        match = re.search(rf"#define\s+{name}\s+(\d+)", self.source)
        self.assertIsNotNone(match, f"{name} not found in {FIRMWARE_MAIN}")
        return int(match.group(1))

    def test_servo_defaults_match(self):
        match = re.search(r"SERVO_DEFAULTS\[\]\s*=\s*\{([^}]*)\}", self.source)
        self.assertIsNotNone(match, "SERVO_DEFAULTS not found in firmware")
        firmware = [int(v) for v in match.group(1).split(",")]
        self.assertEqual(protocol.SERVO_DEFAULTS, firmware)

    def test_angle_range_matches(self):
        self.assertEqual(protocol.MIN_ANGLE, self.define("MIN_ANGLE"))
        self.assertEqual(protocol.MAX_ANGLE, self.define("MAX_ANGLE"))

    def test_firmware_registers_every_command(self):
        for name in ("s", "SAVE", "RUN", "PAUSE", "DEFAULT", "RESET"):
            self.assertRegex(self.source, rf'commands\.add\(F\("{name}"\)', name)

    def test_counts_and_baud_rate_match(self):
        self.assertEqual(protocol.SERVO_COUNT, self.define("SERVO_COUNT"))
        self.assertEqual(protocol.MAX_STEPS, self.define("MAX_STEPS"))
        self.assertEqual(protocol.DEFAULT_BAUD_RATE, self.define("SERIAL_BAUD"))


if __name__ == "__main__":
    unittest.main()
