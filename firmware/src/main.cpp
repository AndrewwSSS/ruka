#include <SoftwareSerial.h>
#include <Arduino.h>
#include "ServoManager.h"
#include "PCA9685Servo.h"
#include "PlaybackManager.h"

#define BLUETOOTH_RX_PIN 13
#define BLUETOOTH_TX_PIN 12
#define SERVO_PWM_FREQ_HZ 50        // standard analog servo frequency
#define SERVO_ROTATION_DELAY_MS 20  // ms between 1-degree steps; lower = faster servo sweep
#define SERVO_COUNT 6
#define MAX_STEPS 50
#define SERIAL_BAUD 9600
#define BLUETOOTH_BAUD 9600
#define BLUETOOTH_TIMEOUT_MS 20

Adafruit_PWMServoDriver pwm; // I2C: SDA -> A4, SCL -> A5 (Uno hardware I2C default)
ServoManager arm(SERVO_COUNT);

SoftwareSerial Bluetooth(BLUETOOTH_RX_PIN, BLUETOOTH_TX_PIN);

PlaybackManager playback(MAX_STEPS, SERVO_COUNT);

String dataIn = "";

void handleCommand(String& cmd);
void onServoReached(uint8_t id);
void readCommandsFrom(Stream& port, const __FlashStringHelper* label);

void setup() {
    Serial.begin(SERIAL_BAUD);
    Bluetooth.begin(BLUETOOTH_BAUD);
    Bluetooth.setTimeout(BLUETOOTH_TIMEOUT_MS);
    Serial.println("Bluetooth ready!");
    delay(20);

    pwm.begin();
    pwm.setPWMFreq(SERVO_PWM_FREQ_HZ);

    const uint8_t SERVO_CHANNELS[] = {0, 1, 2, 13, 14, 15}; // PCA9685 output channels
    const uint8_t SERVO_DEFAULTS[] = {90, 100, 100, 90, 70, 90};

    for (uint8_t i = 0; i < SERVO_COUNT; i++) {
        arm.addMotor(
            new PCA9685Servo(pwm, SERVO_CHANNELS[i], SERVO_DEFAULTS[i], SERVO_ROTATION_DELAY_MS)
        );
    }

    arm.begin();
    arm.onReached(onServoReached);
}

void loop() {
    arm.update();

    readCommandsFrom(Bluetooth, F("BT -> "));
    readCommandsFrom(Serial, F("USB -> "));

    playback.update(arm);
}


void readCommandsFrom(Stream& port, const __FlashStringHelper* label) {
    while (port.available() > 0) {
        dataIn = port.readStringUntil(';');
        dataIn.trim();
        if (dataIn.length() > 0) {
            Serial.print(label);
            Serial.println(dataIn);
            handleCommand(dataIn);
        }
    }
}

void handleCommand(String& cmd) {
    // s1120 → move servo 1 to 120°, s2090 → servo 2 to 90°, etc.
    if (cmd.startsWith("s") && cmd.length() >= 3) {
        int id = cmd.charAt(1) - '1'; // '1'–'6' → index 0–5
        if (id >= 0 && id < (int)SERVO_COUNT) {
            arm.setAngle(id, cmd.substring(2).toInt());
            return;
        }
    }

    if (cmd == "SAVE") {
        playback.save(arm);
        return;
    }

    if (cmd == "RUN") {
        playback.run(arm);
        return;
    }

    if (cmd == "PAUSE") {
        playback.pause();
        return;
    }

    if (cmd == "DEFAULT") {
        arm.setDefaultAngles();
        return;
    }

    if (cmd == "RESET") {
        playback.reset();
        return;
    }
}

void onServoReached(uint8_t id) {
    playback.onServoReached(id);
}
