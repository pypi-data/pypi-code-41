import umachine
from .pin import Pin

class Signal(Pin):

    def __init__(self, no, inverted=False, **kwargs):
        self.pin = Pin.__init__(self, no, **kwargs)
        self.inverted = inverted

    def value(self, v=None):
        if v is None:
            return 1 - Pin.value(self)
        Pin.value(self, 1 - v)
