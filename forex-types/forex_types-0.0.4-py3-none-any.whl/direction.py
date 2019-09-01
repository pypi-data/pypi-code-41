"""Represents direction of trade."""


LONG_STRINGS = {"long", "buy"}
SHORT_STRINGS = {"short", "sell"}


class Direction:
    LONG = "LONG"
    SHORT = "SHORT"

    @staticmethod
    def from_string(string: str):
        lower = string.lower()
        if lower in LONG_STRINGS:
            return Direction.LONG
        elif lower in SHORT_STRINGS:
            return Direction.SHORT
        else:
            raise ValueError(
                f"Direction string not recognized: {lower}"
            )



