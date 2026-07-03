#pragma once
#include "ServoMotor.h"

typedef void (*ServoReachedCallback)(uint8_t id);

class ServoManager {
public:
    ServoManager(const uint8_t* pins, const int* defaultAngles, uint8_t n) {
        count = n;
        reachedCallback = nullptr;

        servos    = new ServoMotor*[count];
        prevState = new ServoMotor::State[count];

        for (uint8_t i = 0; i < count; i++) {
            servos[i]    = new ServoMotor(pins[i], defaultAngles[i]);
            prevState[i] = ServoMotor::HOLD;
        }
    }

    ~ServoManager() {
        for (uint8_t i = 0; i < count; i++) {
            delete servos[i];
        }
        delete[] servos;
        delete[] prevState;
    }

    void begin() {
        for (uint8_t i = 0; i < count; i++) servos[i]->begin();
    }

    void update() {
        for (uint8_t i = 0; i < count; i++) {
            bool wasMoving = prevState[i] != ServoMotor::HOLD;
            servos[i]->update();

            ServoMotor::State now = servos[i]->getState();

            if (wasMoving && now == ServoMotor::HOLD && reachedCallback) {
                reachedCallback(i);
            }

            prevState[i] = now;
        }
    }

    void setDefaultAngles() {
        for (uint8_t i = 0; i < count; i++) servos[i]->setDefaultAngle();
    }

    void setAngle(uint8_t id, int angle) {
        if (id < count) servos[id]->setAngle(angle);
    }

    int getAngle(uint8_t id) const {
        return (id < count) ? servos[id]->getAngle() : -1;
    }

    ServoMotor::State getState(uint8_t id) const {
        return (id < count) ? servos[id]->getState() : ServoMotor::HOLD;
    }

    bool isHold(uint8_t id) const {
        return (id < count) ? (servos[id]->getState() == ServoMotor::HOLD) : true;
    }

    bool allHold() const {
        for (uint8_t i = 0; i < count; i++) {
            if (servos[i]->getState() != ServoMotor::HOLD) return false;
        }
        return true;
    }

    void setAngles(const uint8_t* ids, const int* angles, uint8_t n) {
        for (uint8_t i = 0; i < n; i++) setAngle(ids[i], angles[i]);
    }

    void onReached(ServoReachedCallback cb) { reachedCallback = cb; }

    uint8_t size() const { return count; }

    ServoMotor& operator[](uint8_t id) { return *servos[id]; }

private:
    ServoMotor**        servos;
    ServoMotor::State*  prevState;
    uint8_t             count;
    ServoReachedCallback reachedCallback;
};
