

def get_magnitude(value: int) -> int:
    """Get magnitude of an integer

    (e.g. number of digits when integer is represented normally).
    """
    magnitude = 0
    reduction = value
    while reduction:
        reduction //= 10
        magnitude += 1
    return magnitude


def int_round(value: int, sig: int) -> int:
    """Round integer to integer with sig significant places.

    e.g. int_round(123456, 3) -> 123000
    """
    # Can't make sense of having negative significant figures.
    assert sig >= 0
    # No significant places is a rather special case.
    if sig == 0:
        return 0
    # If we are still here, we need to know how many decimal
    # places integer has to know how to round it.
    magnitude = get_magnitude(value)
    # Now we are set to round
    rounding_level = sig - magnitude  # will be negative
    return round(value, rounding_level)

