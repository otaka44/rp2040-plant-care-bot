import time

import analogio
import digitalio


class MoistureSensor:
    """Analog moisture sensor reader with calibration support."""

    def __init__(
        self,
        analog_pin,
        dry_raw=52000,
        wet_raw=20000,
        vref=3.3,
        vcc_pin=None,
        gnd_pin=None,
    ):
        self._adc = analogio.AnalogIn(analog_pin)
        self._dry_raw = dry_raw
        self._wet_raw = wet_raw
        self._vref = vref
        self._vcc = None
        self._gnd = None

        if vcc_pin is not None:
            self._vcc = digitalio.DigitalInOut(vcc_pin)
            self._vcc.direction = digitalio.Direction.OUTPUT
            self._vcc.value = True

        if gnd_pin is not None:
            self._gnd = digitalio.DigitalInOut(gnd_pin)
            self._gnd.direction = digitalio.Direction.OUTPUT
            self._gnd.value = False

    @property
    def dry_raw(self):
        return self._dry_raw

    @property
    def wet_raw(self):
        return self._wet_raw

    def set_calibration(self, dry_raw=None, wet_raw=None):
        if dry_raw is not None:
            self._dry_raw = int(dry_raw)
        if wet_raw is not None:
            self._wet_raw = int(wet_raw)

    def read_raw(self):
        return self._adc.value

    def raw_to_voltage(self, raw):
        return (raw / 65535) * self._vref

    def read_voltage(self):
        return self.raw_to_voltage(self.read_raw())

    def raw_to_percent(self, raw):
        denominator = self._dry_raw - self._wet_raw
        if denominator == 0:
            return 0.0
        percent = ((self._dry_raw - raw) / denominator) * 100.0
        if percent < 0:
            return 0.0
        if percent > 100:
            return 100.0
        return percent

    def read_percent(self):
        return self.raw_to_percent(self.read_raw())

    def read_raw_stabilized(self, sample_count=5, interval_sec=0.02):
        if sample_count <= 1:
            return self.read_raw()

        samples = []
        for index in range(sample_count):
            samples.append(self.read_raw())
            if interval_sec > 0 and index < sample_count - 1:
                time.sleep(interval_sec)

        samples.sort()
        middle = sample_count // 2
        if sample_count % 2 == 1:
            return samples[middle]
        return int((samples[middle - 1] + samples[middle]) / 2)

    def read_percent_stabilized(self, sample_count=5, interval_sec=0.02):
        return self.raw_to_percent(
            self.read_raw_stabilized(
                sample_count=sample_count, interval_sec=interval_sec
            )
        )

    def deinit(self):
        self._adc.deinit()
        if self._vcc is not None:
            self._vcc.value = False
            self._vcc.deinit()
        if self._gnd is not None:
            self._gnd.value = False
            self._gnd.deinit()
