import time

import board

from lib.load_switch import LoadSwitch
from lib.moisture_sensor import MoistureSensor
from lib.piezo_speaker import PiezoSpeaker
from lib.servo_controller import ServoController


# Hardware pin mapping (RP2040-Zero + schematic in README)
SERVO_SIGNAL_PIN = board.GP9
LOAD_SWITCH_PIN = board.GP4
MOISTURE_ANALOG_PIN = board.GP26
MOISTURE_VCC_PIN = board.GP27
MOISTURE_GND_PIN = board.GP28

# Set to None if speaker is not mounted yet.
SPEAKER_PIN = None

# Moisture calibration (adjust later from measured values)
DRY_RAW = 51788
WET_RAW = 25795

# Decision thresholds for soil condition [percent]
DRY_THRESHOLD = 35.0
WET_THRESHOLD = 70.0

# Servo target angles by soil state
ANGLE_DRY = 90
ANGLE_MOIST = 30
ANGLE_WET = 150

# Main loop interval [seconds]
READ_INTERVAL_SEC = 5.0

# Multi-sample stabilization for noisy moisture readings.
MOISTURE_SAMPLE_COUNT = 5
MOISTURE_SAMPLE_INTERVAL_SEC = 0.02


def classify_moisture(percent):
    if percent < DRY_THRESHOLD:
        return "dry"
    if percent >= WET_THRESHOLD:
        return "wet"
    return "moist"


def angle_for_state(state):
    if state == "dry":
        return ANGLE_DRY
    if state == "wet":
        return ANGLE_WET
    return ANGLE_MOIST


def play_effect(speaker, state):
    if speaker is None:
        return
    if state == "dry":
        speaker.play_dry_effect()
    elif state == "wet":
        speaker.play_wet_effect()
    else:
        speaker.play_humid_effect()


def main():
    load_switch = LoadSwitch(LOAD_SWITCH_PIN, active_high=True, initial_on=False)
    servo = ServoController(SERVO_SIGNAL_PIN)
    sensor = MoistureSensor(
        MOISTURE_ANALOG_PIN,
        dry_raw=DRY_RAW,
        wet_raw=WET_RAW,
        vcc_pin=MOISTURE_VCC_PIN,
        gnd_pin=MOISTURE_GND_PIN,
    )
    speaker = PiezoSpeaker(SPEAKER_PIN) if SPEAKER_PIN is not None else None

    previous_state = None
    print("Soil robot start")
    print("Press Ctrl+C in Thonny shell to stop")

    try:
        while True:
            raw = sensor.read_raw_stabilized(
                sample_count=MOISTURE_SAMPLE_COUNT,
                interval_sec=MOISTURE_SAMPLE_INTERVAL_SEC,
            )
            voltage = sensor.raw_to_voltage(raw)
            percent = sensor.raw_to_percent(raw)
            state = classify_moisture(percent)

            print(
                "raw={:5d} voltage={:.3f}V moisture={:5.1f}% state={}".format(
                    raw, voltage, percent, state
                )
            )

            if state != previous_state:
                target_angle = angle_for_state(state)
                # Power servo only when moving for battery saving.
                load_switch.on()
                time.sleep(0.15)
                servo.set_angle(target_angle, settle_sec=0.35)
                load_switch.off()
                play_effect(speaker, state)
                print("servo -> {} deg".format(target_angle))
                previous_state = state

            time.sleep(READ_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        load_switch.off()
        servo.off()
        servo.deinit()
        sensor.deinit()
        if speaker is not None:
            speaker.deinit()
        load_switch.deinit()


main()
