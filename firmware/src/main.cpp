#include <SoftwareSerial.h>
#include <Arduino.h>
#include <CommandDispatcher.h>
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
#define MIN_ANGLE 0
#define MAX_ANGLE 180

Adafruit_PWMServoDriver pwm; // I2C: SDA -> A4, SCL -> A5 (Uno hardware I2C default)
ServoManager arm(SERVO_COUNT);

SoftwareSerial Bluetooth(BLUETOOTH_RX_PIN, BLUETOOTH_TX_PIN);

PlaybackManager playback(MAX_STEPS, SERVO_COUNT);

// Errors and usage lines go to USB; Bluetooth is send-only.
CommandDispatcher<8> commands(Serial);
LineReader<16>       usb(Serial, ';');
LineReader<16>       bluetooth(Bluetooth, ';');

// s <servo> <angle>: servo 1-6, angle clamped to 0-180.
static void cmdServo(const CommandArgs& args) {
    long servo = args.getLong(0);
    if (servo < 1 || servo > SERVO_COUNT) {
        Serial.println(F("servo must be 1-6"));
        return;
    }
    // Clamp before narrowing: int is 16 bits on the Uno.
    long angle = constrain(args.getLong(1), MIN_ANGLE, MAX_ANGLE);
    arm.setAngle((uint8_t)(servo - 1), (int)angle);
}

static void cmdSave(const CommandArgs&)    { playback.save(arm); }
static void cmdRun(const CommandArgs&)     { playback.run(arm); }
static void cmdPause(const CommandArgs&)   { playback.pause(); }
static void cmdDefault(const CommandArgs&) { arm.setDefaultAngles(); }
static void cmdReset(const CommandArgs&)   { playback.reset(); }

static void onServoReached(uint8_t id) {
    playback.onServoReached(id);
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    Bluetooth.begin(BLUETOOTH_BAUD);
    Serial.println(F("Bluetooth ready!"));
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

    commands.add(F("s"), F("nn"), cmdServo);
    commands.add(F("SAVE"), cmdSave);
    commands.add(F("RUN"), cmdRun);
    commands.add(F("PAUSE"), cmdPause);
    commands.add(F("DEFAULT"), cmdDefault);
    commands.add(F("RESET"), cmdReset);
}

void loop() {
    arm.update();

    bluetooth.poll(commands);
    usb.poll(commands);

    playback.update(arm);
}
