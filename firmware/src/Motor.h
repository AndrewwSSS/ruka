#pragma once
#include <Arduino.h>


// Common interface for any angle-driven actuator (hobby servo, PCA9685-driven
// servo, geared stepper acting as a joint, ...). Concrete motor types plug
// into ServoManager/Robot code by implementing begin() (hardware setup) and
// writeAngle() (a single hardware write); the gradual move-to-target loop,
// target clamping, default angle, state tracking and debug flag all live
// here so they aren't duplicated per motor type.
class Motor {
public:
    enum State {
        MOVING,
        HOLD
    };

    virtual ~Motor() = default;

    // Attaches/initializes the underlying hardware and drives it to defaultAngle.
    virtual void begin() = 0;

    // Advances the motor one step towards target_angle. Must be called repeatedly
    // (e.g. from loop()). Shared by every motor type; only the hardware write
    // (writeAngle) differs between them.
    void update() {
        if (current_angle == target_angle) {
            setState(HOLD);
            return;
        }

        unsigned long now = millis();
        if (now - lastMove < ROTATION_DELAY) return;

        current_angle += (current_angle < target_angle) ? 1 : -1;
        writeAngle(current_angle);
        lastMove = now;
        setState(MOVING);

        if (DEBUG) {
            Serial.println("Current angle: " + String(current_angle));
        }
    }

    void setAngle(uint8_t angle) {
        if (angle < MIN_ANGLE) angle = MIN_ANGLE;
        if (angle > MAX_ANGLE) angle = MAX_ANGLE;

        this->target_angle = angle;

        if (DEBUG) {
            Serial.println("Setting target angle to " + String(target_angle));
        }
    }

    void setDefaultAngle() {
        setAngle(this->defaultAngle);
    }

    uint8_t getAngle() const {
        return this->current_angle;
    }

    void toggleDebug() {
        this->DEBUG = !this->DEBUG;
    }

    bool getDebug() const {
        return this->DEBUG;
    }

    State getState() const {
        return this->state;
    }

    // True exactly once, the first time this is polled after the motor
    // settles into HOLD. Lets a manager fire a "reached" callback without
    // keeping its own shadow copy of every motor's previous state.
    bool reachedTarget() {
        bool r = justReached;
        justReached = false;
        return r;
    }

protected:
    explicit Motor(uint8_t defaultAngle)
        : current_angle(defaultAngle),
          target_angle(defaultAngle),
          defaultAngle(defaultAngle),
          lastMove(0),
          state(HOLD),
          justReached(false) {}

    static constexpr int DEFAULT_ANGLE = 45;
    static constexpr int MIN_ANGLE = 0;
    static constexpr int MAX_ANGLE = 180;
    static constexpr unsigned long ROTATION_DELAY = 20; // ms

    // Derived classes report motion state through here instead of writing
    // `state` directly, so the MOVING -> HOLD edge (used by reachedTarget())
    // is only ever detected in one place.
    void setState(State newState) {
        if (newState == HOLD && state != HOLD) {
            justReached = true;
        }
        state = newState;
    }

    // Physically drives the actuator to the given angle. Called from
    // update() on every step and from begin() to reach the initial position.
    virtual void writeAngle(uint8_t angle) = 0;

    bool DEBUG = false;

    uint8_t current_angle;
    uint8_t target_angle;
    uint8_t defaultAngle;
    unsigned long lastMove;

private:
    State state;
    bool justReached;
};
