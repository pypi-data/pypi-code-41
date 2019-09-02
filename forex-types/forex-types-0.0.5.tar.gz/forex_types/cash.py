"""Cash objects are decimal amount in a currency."""

from decimal import Decimal

from forex_types.currency import Currency


class Cash:

    def __init__(self, value: Decimal, currency: Currency):
        self.value = Decimal(value)
        self.currency = currency

    def __str__(self):
        return f"{self.value} {self.currency}"

    def nearest_dollar(self):
        if self.currency == Currency.JPY:
            return Cash(round(self.value.shift(-2), 0) * 100, Currency.JPY)
        else:
            return Cash(round(self.value, 0), self.currency)

    def nearest_cent(self):
        if self.currency == Currency.JPY:
            return Cash(round(self.value, 0), Currency.JPY)
        else:
            return Cash(round(self.value, 2), self.currency)


