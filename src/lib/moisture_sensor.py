import analogio


class MoistureSensor:
    """Analog moisture sensor reader with calibration support."""

    def __init__(self, analog_pin, dry_raw=52000, wet_raw=20000, vref=3.3):
        self._adc = analogio.AnalogIn(analog_pin)
        self._dry_raw = dry_raw
        self._wet_raw = wet_raw
        self._vref = vref

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

    def read_voltage(self):
        return (self._adc.value / 65535) * self._vref

    def read_percent(self):
        raw = self.read_raw()
        denominator = self._dry_raw - self._wet_raw
        if denominator == 0:
            return 0.0
        percent = ((self._dry_raw - raw) / denominator) * 100.0
        if percent < 0:
            return 0.0
        if percent > 100:
            return 100.0
        return percent

    def deinit(self):
        self._adc.deinit()
