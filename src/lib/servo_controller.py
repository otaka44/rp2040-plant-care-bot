import time

import pwmio


class ServoController:
    """Simple 50Hz servo controller for CircuitPython."""

    def __init__(
        self,
        pin,
        min_angle=0,
        max_angle=180,
        min_pulse_us=500,
        max_pulse_us=2400,
        frequency=50,
    ):
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._min_pulse_us = min_pulse_us
        self._max_pulse_us = max_pulse_us
        self._period_us = int(1_000_000 / frequency)
        self._pwm = pwmio.PWMOut(pin, duty_cycle=0, frequency=frequency)

    def _clamp_angle(self, angle):
        if angle < self._min_angle:
            return self._min_angle
        if angle > self._max_angle:
            return self._max_angle
        return angle

    def _angle_to_duty(self, angle):
        angle = self._clamp_angle(angle)
        ratio = (angle - self._min_angle) / (self._max_angle - self._min_angle)
        pulse_us = (
            self._min_pulse_us + (self._max_pulse_us - self._min_pulse_us) * ratio
        )
        return int((pulse_us / self._period_us) * 65535)

    def set_angle(self, angle, settle_sec=0.25):
        self._pwm.duty_cycle = self._angle_to_duty(angle)
        if settle_sec > 0:
            time.sleep(settle_sec)

    def off(self):
        self._pwm.duty_cycle = 0

    def deinit(self):
        self._pwm.deinit()
