"""Price class."""

from decimal import Decimal
from statistics import mean


class BasePrice:
    """Common parent of Price and NinjaPrice"""

    # Prices outside these limits are considered errors.
    MIN = Decimal("0.1")   # minimum for standard quote currencies
    MAX = Decimal("10.0")  # maximum for standard quote currencies
    NINJA_MIN = Decimal("15.00")  # minimum for Japanese Yen.
    NINJA_MAX = Decimal("1000.00")  # maximum for Japanese Yen.

    PIP_PER_UNIT = 10000
    NINJA_PIP_PER_UNIT = 100

    def __init__(self, value):
        self.value = None
        self.pips = None

    def __str__(self):
        return str(self.value)

    @staticmethod
    def mean(price_list):
        """Get mean average Price from list of prices."""
        decimal_values = [_.value for _ in price_list]
        decimal_mean = mean(decimal_values)
        return Price(decimal_mean)

    def __eq__(self, other):
        if not isinstance(other, BasePrice):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, BasePrice):
            return NotImplemented
        return self.value < other.value


class Price(BasePrice):

    def __init__(self, value):
        BasePrice.__init__(self, value)
        self.value = Decimal(round(Decimal(value), 5))
        self.pips = round(Decimal(self.value * self.PIP_PER_UNIT), 1)

    def __new__(cls, value):
        value = Decimal(value)
        if cls.MIN <= value <= cls.MAX:
            return super(Price, cls).__new__(cls)
        elif cls.NINJA_MIN <= value <= cls.NINJA_MAX:
            return NinjaPrice(value)
        else:
            raise ValueError(f"Price out of reasonable range: {value}")

    def add_pips(self, pips: int):
        """Return new Price object adjusted by number of pips."""
        price_delta = Decimal(pips / self.PIP_PER_UNIT)
        return Price(self.value + price_delta)


class NinjaPrice(BasePrice):
    """Variant for when quote currency is Japanese yen."""

    def __init__(self, value):
        BasePrice.__init__(self, value)
        self.value = Decimal(round(Decimal(value), 3))
        self.pips = round(Decimal(self.value * self.NINJA_PIP_PER_UNIT), 1)

    def add_pips(self, pips: int):
        """Return new NinjaPrice object adjusted by number of pips."""
        price_delta = Decimal(pips / self.NINJA_PIP_PER_UNIT)
        return NinjaPrice(self.value + price_delta)
