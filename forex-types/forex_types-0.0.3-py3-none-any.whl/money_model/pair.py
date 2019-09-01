"""Currency pair class. Initialized by string.

Synopsis:
    pair = Pair("eurusd")  # Case insensitive, non letters ignored.
    base = pair.base
    quote = pair.quote
"""

import string

from money_model.currency import Currency


class Pair:

    CURRENCIES = {
        "aud": Currency.AUD,
        "cad": Currency.CAD,
        "chf": Currency.CHF,
        "eur": Currency.EUR,
        "gbp": Currency.GBP,
        "jpy": Currency.JPY,
        "nzd": Currency.NZD,
        "usd": Currency.USD,
    }
    LETTERS = {_ for _ in string.ascii_lowercase}

    def __init__(self, name: str):
        letters = [_ for _ in name.lower() if _ in self.LETTERS]
        self.name = "".join(letters)
        if len(self.name) != 6:
            raise ValueError(f"Unknown pair: {self.name}")
        base_name = "".join(letters[:3])
        quote_name = "".join(letters[3:])
        if base_name not in self.CURRENCIES:
            raise ValueError(f"Unknown base in pair: {self.name}")
        if quote_name not in self.CURRENCIES:
            raise ValueError(f"Unknown quote in pair: {self.name}")
        self.base = self.CURRENCIES[base_name]
        self.quote = self.CURRENCIES[quote_name]
        if self.base.precedence >= self.quote.precedence:
            raise ValueError(f"Bad permutation of base and quote in pair: {self.name}")

    @staticmethod
    def from_currency(base: Currency, quote: Currency):
        """Make pair object from two currency objects or strings."""
        return Pair(str(base) + str(quote))

    def __hash__(self):
        return hash((self.base, self.base.currency))

    def __str__(self):
        """String representation intentionally matches Oanda v20"""
        return f"{self.base}_{self.quote}"

    def __eq__(self, other):
        if not isinstance(other, Pair):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other):
        if not isinstance(other, Pair):
            return NotImplemented
        if self.base < other.base:
            return True
        return self.quote < other.quote

    def camel(self):
        """Return pair name in camel case like: AudUsd"""
        return f"{self.base.name.title()}{self.quote.name.title()}"

    @classmethod
    def iter_pairs(cls):
        base_list = Currency.get_list()  # sorted by precedence.
        quote_list = Currency.get_list() # e.g. EUR -> JPY
        base_list.pop()    # Last currency will not be a base.
        quote_list.pop(0)  # First currency will not be a quote.
        while base_list:
            base = base_list.pop(0)
            for quote in quote_list:
                yield cls(f"{base}{quote}")
            quote_list.pop(0)


