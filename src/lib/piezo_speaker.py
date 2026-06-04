import time

import pwmio


class PiezoSpeaker:
    """Optional piezo speaker helper for simple effects."""

    def __init__(self, pin):
        self._pwm = pwmio.PWMOut(pin, duty_cycle=0, frequency=440)

    def tone(self, frequency_hz, duration_sec=0.1, duty_cycle=32768):
        self._pwm.frequency = int(frequency_hz)
        self._pwm.duty_cycle = int(duty_cycle)
        time.sleep(duration_sec)
        self._pwm.duty_cycle = 0

    def play_dry_effect(self):
        self.tone(523, 0.08)
        self.tone(659, 0.08)
        self.tone(784, 0.10)

    def play_wet_effect(self):
        self.tone(784, 0.08)
        self.tone(659, 0.08)
        self.tone(523, 0.12)

    def play_humid_effect(self):
        self.tone(440, 0.08)
        self.tone(494, 0.08)
        self.tone(523, 0.10)

    def deinit(self):
        self._pwm.deinit()
