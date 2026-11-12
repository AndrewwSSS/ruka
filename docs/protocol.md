# Serial protocol

The desktop app and the firmware talk over a serial port: USB, or an HC-05
Bluetooth module paired with the computer. Both appear to the OS as an ordinary
serial port at **9600 baud**.

- Firmware side: [`firmware/src/main.cpp`](../firmware/src/main.cpp) and
  [`PlaybackManager.h`](../firmware/src/PlaybackManager.h).
- App side: [`desktop/ruka_app/core/protocol.py`](../desktop/ruka_app/core/protocol.py).

## Commands

Commands are words separated by spaces, each command terminated with `;`. Names
are case-insensitive; line breaks and other control characters are ignored. The
firmware parses them with
[CommandDispatcher](https://github.com/AndrewwSSS/CommandDispatcher), which
checks the arguments before a command runs.

| Command | Example | Does |
| --- | --- | --- |
| `s <servo> <angle>` | `s 1 120;` | move servo 1–6 to an angle; values outside 0–180° are clamped |
| `SAVE` | `SAVE;` | record the current angles of all servos as the next step (up to 50) |
| `RUN` | `RUN;` | play the recorded steps in order; resumes if paused |
| `PAUSE` | `PAUSE;` | pause playback |
| `DEFAULT` | `DEFAULT;` | move every servo to its default angle |
| `RESET` | `RESET;` | stop playback and delete all recorded steps |

Playback moves to the next step once every servo has reached its target.

## Status lines

The firmware answers on **USB only**, one line each:

| Line | Meaning |
| --- | --- |
| `Saved step <n>` | a step was recorded; n steps are stored |
| `Playing step <i>/<n>` | playback moved to step i of n |
| `Current playback step reached.` | every servo reached the current step |
| `Playback finished.` | the last step was reached |
| `Reset.` | the recorded steps were deleted |
| `usage: s <number> <number>` | a command's arguments were missing or not numbers |
| `servo must be 1-6` | the servo number was out of range |
| `unknown command: <word>` | no command has that name |
| `line too long, at most 15 characters` | the line was discarded |

The app tracks the step count and playback state from these lines, so they are
matched literally and must not be translated.

**Bluetooth is send-only:** the HC-05 module is connected through
SoftwareSerial, and the firmware never writes status lines back to it. A
Bluetooth session can control the arm, but the app receives no status.

## Shared constants

| Constant | Value | Firmware | App |
| --- | --- | --- | --- |
| Servos | 6 | `SERVO_COUNT` | `SERVO_COUNT` |
| Max recorded steps | 50 | `MAX_STEPS` | `MAX_STEPS` |
| Baud rate | 9600 | `SERIAL_BAUD`, `BLUETOOTH_BAUD` | `DEFAULT_BAUD_RATE` |
| Angle range | 0–180° | `MIN_ANGLE`, `MAX_ANGLE` | `MIN_ANGLE`, `MAX_ANGLE` |
| Default angles | 90, 100, 100, 90, 70, 90 | `SERVO_DEFAULTS` | `SERVO_DEFAULTS` |

`desktop/tests/test_protocol.py` reads these from the firmware source and fails
if the app's values differ, or if the firmware stops registering a command the
app sends.
