import time

import board

from lib.load_switch import LoadSwitch
from lib.servo_controller import ServoController


# Pin mapping (RP2040-Zero)
SERVO_SIGNAL_PIN = board.GP9

# If servo power is switched by a transistor/MOSFET, set to True.
USE_LOAD_SWITCH = True
LOAD_SWITCH_PIN = board.GP4

# Calibration movement settings
START_ANGLE = 90
END_ANGLE = 150
STEP_ANGLE = 60
HOLD_SEC = 2.0


def build_sweep_angles(start_angle, end_angle, step_angle):
    forward = list(range(start_angle, end_angle + 1, step_angle))
    backward = list(range(end_angle - step_angle, start_angle, -step_angle))
    return forward + backward


def main():
    load_switch = None
    if USE_LOAD_SWITCH:
        load_switch = LoadSwitch(LOAD_SWITCH_PIN, active_high=True, initial_on=False)
        load_switch.on()
        time.sleep(0.2)

    servo = ServoController(SERVO_SIGNAL_PIN)
    angles = build_sweep_angles(START_ANGLE, END_ANGLE, STEP_ANGLE)

    print("Servo calibration start")
    print("Move: {} -> {} (step {} deg)".format(START_ANGLE, END_ANGLE, STEP_ANGLE))
    print("Press Ctrl+C in Thonny shell to stop")

    try:
        while True:
            for angle in angles:
                servo.set_angle(angle, settle_sec=0)
                print("servo -> {} deg".format(angle))
                time.sleep(HOLD_SEC)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        servo.off()
        servo.deinit()
        if load_switch is not None:
            load_switch.off()
            load_switch.deinit()


main()
