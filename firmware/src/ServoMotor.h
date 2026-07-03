#pragma once
#include <Servo.h>
#include <Arduino.h>


class ServoMotor {
public:
    enum State {
        MOVING_UP,
        MOVING_DOWN,
        HOLD
    };
    

    ServoMotor(uint8_t pin, int defaultAngle = DEFAULT_ANGLE) {
        this->servoPin = pin;
        this->current_angle = defaultAngle;
        this->target_angle = defaultAngle;
        this->defaultAngle = defaultAngle;
        this->lastMove = 0;
        this->state = HOLD;
    }

    ~ServoMotor() {
        servo.detach();
    }

    void begin() {
        Serial.println("turning servo to default angle: " + String(target_angle) + " on pin " + String(servoPin));

        servo.attach(servoPin);
        servo.write(target_angle);

        // Wait for the servo to reach the default position
        delay(1000);

        state = HOLD;
    }

    void update() {
        unsigned long now = millis();
        if (current_angle < target_angle && now - lastMove >= ROTATION_DELAY) {

            if (state == HOLD)
                servo.attach(servoPin);

            current_angle += 1;
            servo.write(current_angle);
            lastMove = now;
            state = MOVING_UP;

            if (DEBUG) {
                Serial.println("Current angle: " + String(current_angle) + " pin: " + String(servoPin));
            }
        } else if (current_angle > target_angle && now - lastMove >= ROTATION_DELAY) {

            if (state == HOLD)
                servo.attach(servoPin);

            current_angle -= 1;
            servo.write(current_angle);
            lastMove = now;
            state = MOVING_DOWN;

            if (DEBUG) {
                Serial.println("Current angle: " + String(current_angle) + " pin: " + String(servoPin));
            }

        }

        if (current_angle == target_angle && state != HOLD) {
            state = HOLD;
            //servo.detach();
        }
    }

    void setAngle(int angle) {
        if (angle < MIN_ANGLE) angle = MIN_ANGLE;
        if (angle > MAX_ANGLE) angle = MAX_ANGLE;

        this->target_angle = angle;

        if (DEBUG) {
            Serial.println("Setting target angle to " + String(target_angle) + " for pin " + String(servoPin));
        }
    }

    void setDefaultAngle() {
        setAngle(this->defaultAngle);
    }

    int getAngle() const {
        return this->current_angle;
    }

    void toggleDebug() {
        this->DEBUG = !this->DEBUG;
        Serial.println("ServoMotor DEBUG is now " + String(this->DEBUG ? "ON" : "OFF") + " for pin " + String(this->servoPin));
    }

    bool getDebug() const {
        return this->DEBUG;
    }

    State getState() const {
        return this->state;
    }

    bool turnUP() {
        if (this->state == HOLD && this->current_angle < this->MAX_ANGLE) {
            this->target_angle = this->MAX_ANGLE;
            return true;
        }
        return false;
    }

    bool turnDOWN() {
        if (this->state == HOLD && this->current_angle > this->MIN_ANGLE) {
            this->target_angle = this->MIN_ANGLE;
            return true;
        }
        return false;
    }

    bool toggle() {

        if (this->state != HOLD) {
            return false; // Ignore if currently moving
        }

        if (this->current_angle == this->MIN_ANGLE) {
            this->target_angle = this->MAX_ANGLE;
        } else if (this->current_angle == this->MAX_ANGLE) {
            this->target_angle = this->MIN_ANGLE;
        } else {
            this->target_angle = this->DEFAULT_ANGLE;
        }

        return true;
    }

private:
    static constexpr int DEFAULT_ANGLE = 45;
    static constexpr int MIN_ANGLE = 0;
    static constexpr int MAX_ANGLE = 180;
    static constexpr int ROTATION_DELAY = 20; // ms

    Servo servo;
    uint8_t servoPin;
    bool DEBUG = false;

    int current_angle;
    int target_angle;
    int defaultAngle;
    unsigned long lastMove;
    State state;
};
