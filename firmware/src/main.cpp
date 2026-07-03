#include <SoftwareSerial.h>
#include <Arduino.h>
#include "ServoManager.h"

const uint8_t SERVO_PINS[]     = {5, 6, 7, 8, 9, 10};
const int     SERVO_DEFAULTS[] = {90, 90, 90, 90, 90, 90};
const uint8_t SERVO_COUNT      = 6;
const int     MAX_STEPS        = 50;

ServoManager arm(SERVO_PINS, SERVO_DEFAULTS, SERVO_COUNT);

SoftwareSerial Bluetooth(12, 13); // Arduino(RX, TX) - HC-05 Bluetooth (TX, RX)

int  savedPositions[MAX_STEPS][SERVO_COUNT];
int  stepCount      = 0;
bool playbackActive = false;
bool playbackPaused = false;
int  playbackStep   = 0;
bool playbackStepCurrentStepReached = false;
uint8_t playbackStepReachedCount = 0;

String dataIn = "";

void handleCommand(String& cmd);
void runPlaybackStep();
void onServoReached(uint8_t id);

void setup() {
    Serial.begin(9600);
    Bluetooth.begin(9600);
    Bluetooth.setTimeout(20);
    Serial.println("Bluetooth ready!");
    delay(20);
    arm.begin();
    arm.onReached(onServoReached);
}

void loop() {
    arm.update();

    while (Bluetooth.available() > 0) {
        dataIn = Bluetooth.readStringUntil(';');
        dataIn.trim();
        if (dataIn.length() > 0) {
            Serial.print("BT -> ");
            Serial.println(dataIn);
            handleCommand(dataIn);
        }
    }

    while (Serial.available() > 0) {
        dataIn = Serial.readStringUntil(';');
        dataIn.trim();
        if (dataIn.length() > 0) {
            Serial.print("USB -> ");
            Serial.println(dataIn);
            handleCommand(dataIn);
        }
    }

    if (playbackActive && !playbackPaused && playbackStepCurrentStepReached) {
        playbackStepCurrentStepReached = false;
        playbackStepReachedCount = 0;

        playbackStep++;
        if (playbackStep >= stepCount) {
            Serial.println("Playback finished.");
            playbackActive = false;
        } else {
            runPlaybackStep();
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
        if (stepCount < MAX_STEPS) {
            for (uint8_t i = 0; i < SERVO_COUNT; i++) {
                savedPositions[stepCount][i] = arm.getAngle(i);
            }
            stepCount++;
            Serial.println("Saved step " + String(stepCount));
        }
        return;
    }

    if (cmd == "RUN") {
        if (playbackActive && playbackPaused) {
            playbackPaused = false; // resume from pause
        } else if (stepCount > 0) {
            playbackStep   = 0;
            playbackActive = true;
            playbackPaused = false;
            playbackStepCurrentStepReached = false;
            playbackStepReachedCount = 0;
            runPlaybackStep();
        }
        return;
    }

    if (cmd == "PAUSE") {
        playbackPaused = true;
        return;
    }

    if (cmd == "DEFAULT") {
        arm.setDefaultAngles();
        return;
    }

    if (cmd == "RESET") {
        playbackActive = false;
        playbackPaused = false;
        playbackStep   = 0;
        stepCount      = 0;
        playbackStepCurrentStepReached = false;
        playbackStepReachedCount = 0;
        memset(savedPositions, 0, sizeof(savedPositions));
        Serial.println("Reset.");
        return;
    }
}

void runPlaybackStep() {
    if (playbackStep >= stepCount) {
        playbackStep = 0; // loop back to start
    }

    playbackStepCurrentStepReached = false;
    playbackStepReachedCount = 0;

    for (uint8_t i = 0; i < SERVO_COUNT; i++) {
        arm.setAngle(i, savedPositions[playbackStep][i]);
    }
    
    Serial.println("Playing step " + String(playbackStep + 1) + "/" + String(stepCount));
}

void onServoReached(uint8_t id) {
    if (!playbackActive || playbackStepCurrentStepReached) {
        return;
    }

    playbackStepReachedCount++;
    if (playbackStepReachedCount >= SERVO_COUNT) {
        playbackStepCurrentStepReached = true;
        Serial.println("Current playback step reached.");
    }
}
