"""Lot size, in base currency, in batches of 1000 (rounded down)."""

from decimal import Decimal

from forex_types.odd_math import int_round

ZERO = 0
HUNDRED = 100
THOUSAND = 1000
TEN_THOUSAND = 10000
HUNDRED_THOUSAND = 100000
MILLION = 1000000
TEN_MILLION = 10000000
HUNDRED_MILLION = 100000000
BILLION = 1000000000
TEN_BILLION = 10000000000
HUNDRED_BILLION = 100000000000


def get_lot_abbr(size: int) -> str:
    return LotSize(size).get_abbr()


def divide_lot(size: int, num_targets: int) -> list:
    return LotSize(size).divide(num_targets)


class LotSize(int):

    def get_rounded(self, sig: int=2):
        """Round off to sig significant figures.

        For example 1384567 with sig of 2 returns 1400000
        with a sig of 3 it would be 1380000 and so forth.

        Args:
            sig: positive number of significant figures.
        Returns:
            LotSize
        """
        return LotSize(int_round(self, sig))

    @classmethod
    def from_abbr(cls, abbr: str):
        """Get lot size from a string abbreviation."""
        raw_chars = abbr.strip().upper()
        if len(raw_chars) < 2:
            return 0
        last_char = raw_chars[-1]
        if last_char == "K":
            decimal_value = Decimal(raw_chars[:-1]) * THOUSAND
            return LotSize(decimal_value)
        elif last_char == "M":
            decimal_value = Decimal(raw_chars[:-1]) * MILLION
            return LotSize(decimal_value)
        elif last_char == "B":
            decimal_value = Decimal(raw_chars[:-1]) * BILLION
            return LotSize(decimal_value)
        else:
            return LotSize(Decimal(raw_chars))

    def get_abbr(self):
        """Get abbreviated string representation

        Examples:
                            0      "0"
                         1000     "1K"
                       12,000    "12K"
                      123,000   "123K"
                    1,230,000  "1.23M"
                   12,300,000  "12.3M"
                  123,000,000   "123M"
                1,230,000,000  "1.23B"
               12,300,000,000  "1.23B"
              123,000,000,000   "123B"
        """
        if self >= BILLION:
            display = Decimal(self) / BILLION
            return f"{display}B"
        elif self >= MILLION:
            display = Decimal(self) / MILLION
            return f"{display}M"
        elif self >= THOUSAND:
            display = Decimal(self) / THOUSAND
            return f"{display}K"
        else:
            return str(self)

    def _split(self):
        """Helper for divide method.

        Rounds down and splits significant digit part from rest of product.

        For example 1000 returns (1, 1000)
        For example 11000 returns (11, 1000)
        For example 123,000 returns (123, 1000)
        For example 1,230,000 returns (123, 10,000)
        For example 1,000,000 returns (100, 10,000)

        and so forth, with no more than 3 digits in first part, but at 100,000
        and up, at least three digits in first part.
        """
        if self < THOUSAND:
            return self, 1
        elif self <= 12 * THOUSAND:
            return self // HUNDRED, HUNDRED
        elif self < MILLION:
            return self // THOUSAND, THOUSAND
        else:
            digit_string = str(self)
            significant_digits = digit_string[:3]
            zeroes = digit_string[3:]
            return int(significant_digits), int("1" + zeroes)

    def divide(self, num_target: int) -> list:
        """Divide size into sizes for a specific number of targets.

        The division may be a little uneven in order to keep the basic unit
        of lot size the same for example for a lot size of 121K divided
        three ways it would return [40K, 40K, 41K].  Note the extra 1K is
        added to the latter sizes in the list. But the extra size of latter
        values may be larger than 1K for larger sizes. For example with 13.7M
        the extra difference is 0.10M, so that for two targets it would return
        [6.80M, 6.90M].

        Args:
            num_target: int, 1 or more. Number of targets to divide size among.
        Returns:
            list of LotSize objects
        """
        assert num_target > 0
        # Determine how the amount splits up
        num, units = self._split()
        remainder = num % num_target
        usable_num = num - remainder
        partial_num = usable_num // num_target
        # Determine rounded down size and the low and high divided sizes
        low_size = LotSize(partial_num * units)
        high_size = LotSize((partial_num + 1) * units)
        # Determine how many of lower size and how many of higher size
        num_low_size = int(num_target - remainder)
        num_high_size = remainder
        # Assemble our return list
        return_list = []
        for i in range(num_low_size):
            return_list.append(low_size)
        for i in range(num_high_size):
            return_list.append(high_size)
        return return_list
