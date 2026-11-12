#pragma once
#include <Arduino.h>
#include "ServoManager.h"

// Records servo position "steps" and plays them back sequentially, advancing
// to the next step once every servo has reached its target angle (reported
// via onServoReached, wired to ServoManager::onReached).
class PlaybackManager {
public:
    PlaybackManager(uint8_t maxSteps, uint8_t servoCount)
        : maxSteps(maxSteps), servoCount(servoCount) {
        positions = new uint8_t[(uint16_t)maxSteps * servoCount];
    }

    ~PlaybackManager() {
        delete[] positions;
    }

    void save(ServoManager& arm) {
        if (stepCount >= maxSteps) return;

        for (uint8_t i = 0; i < servoCount; i++) {
            positions[stepIndex(stepCount, i)] = arm.getAngle(i);
        }
        stepCount++;
        Serial.print(F("Saved step "));
        Serial.println(stepCount);
    }

    void run(ServoManager& arm) {
        if (active && paused) {
            paused = false; // resume from pause
            return;
        }
        if (stepCount == 0) return;

        step = 0;
        active = true;
        paused = false;
        playStep(arm);
    }

    void pause() {
        paused = true;
    }

    void reset() {
        active = false;
        paused = false;
        step = 0;
        stepCount = 0;
        stepReached = false;
        reachedCount = 0;
        memset(positions, 0, (uint16_t)maxSteps * servoCount);
        Serial.println(F("Reset."));
    }

    // Wire to ServoManager::onReached so each servo arrival counts toward the current step.
    void onServoReached(uint8_t id) {
        if (!active || stepReached) return;

        reachedCount++;
        if (reachedCount >= servoCount) {
            stepReached = true;
            Serial.println(F("Current playback step reached."));
        }
    }

    // Call once per loop() iteration; advances to the next step when the current one completes.
    void update(ServoManager& arm) {
        if (!active || paused || !stepReached) return;

        step++;
        if (step >= stepCount) {
            Serial.println(F("Playback finished."));
            active = false;
        } else {
            playStep(arm);
        }
    }

private:
    uint16_t stepIndex(uint8_t stepIdx, uint8_t servoIdx) const {
        return (uint16_t)stepIdx * servoCount + servoIdx;
    }

    void playStep(ServoManager& arm) {
        if (step >= stepCount) step = 0; // loop back to start

        stepReached = false;
        reachedCount = 0;

        for (uint8_t i = 0; i < servoCount; i++) {
            arm.setAngle(i, positions[stepIndex(step, i)]);
        }

        Serial.print(F("Playing step "));
        Serial.print(step + 1);
        Serial.print('/');
        Serial.println(stepCount);
    }

    uint8_t* positions;
    uint8_t  maxSteps;
    uint8_t  servoCount;
    uint8_t  stepCount    = 0;
    uint8_t  step         = 0;
    bool     active       = false;
    bool     paused       = false;
    bool     stepReached  = false;
    uint8_t  reachedCount = 0;
};
