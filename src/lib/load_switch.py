import digitalio


class LoadSwitch:
    """Control a load switch with one digital pin."""

    def __init__(self, pin, active_high=True, initial_on=False):
        self._active_high = active_high
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.OUTPUT
        self.set(initial_on)

    def set(self, on):
        if self._active_high:
            self._pin.value = bool(on)
        else:
            self._pin.value = not bool(on)

    def on(self):
        self.set(True)

    def off(self):
        self.set(False)

    def deinit(self):
        self._pin.deinit()
