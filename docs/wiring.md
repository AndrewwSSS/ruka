# Wiring

The pins are defined at the top of
[`firmware/src/main.cpp`](../firmware/src/main.cpp). The full diagram is the
Fritzing project [`firmware/fritzing/ruka.fzz`](../firmware/fritzing/ruka.fzz);
the custom parts it uses are in [`firmware/fritzing/parts/`](../firmware/fritzing/parts).

## PCA9685 servo board

The six servos are driven by a PCA9685 16-channel PWM board over I2C, at 50 Hz.

| Uno | PCA9685 |
| --- | --- |
| A4 | SDA |
| A5 | SCL |
| GND | GND |

Power for the boards and the servos is shown in the Fritzing diagram. The
servos draw far more current than the Uno can supply, so the board's servo
power input (V+) needs its own supply, with GND shared with the Uno.

## Servos

| Servo | PCA9685 channel | Default angle |
| --- | --- | --- |
| 1 | 0 | 90° |
| 2 | 1 | 100° |
| 3 | 2 | 100° |
| 4 | 13 | 90° |
| 5 | 14 | 70° |
| 6 | 15 | 90° |

Servo 1 is at the base and servo 6 drives the gripper, as in the desktop app's
diagram. Each servo moves to its default angle at start-up and moves one degree
every 20 ms.

## HC-05 Bluetooth module

The module is connected through SoftwareSerial at 9600 baud:

| Uno | HC-05 |
| --- | --- |
| D13 (RX) | TXD |
| D12 (TX) | RXD |
| GND | GND |

The HC-05's RXD pin uses 3.3 V logic, so a voltage divider between D12 and RXD
is the usual way to connect it to the Uno's 5 V output.

The Uno's USB serial port runs at 9600 baud too. Both ports accept the same
commands; status lines go to USB only (see [protocol.md](protocol.md)).
