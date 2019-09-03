def setBit(x, offset):
    mask = 1 << offset
    return (x | mask)


def clearBit(x, offset):
    mask = ~(1 << offset)
    return (x & mask)


def testBit(x, offset):
    mask = 1 << offset
    if (x & mask):
        return 1
    else:
        return 0


def changeBit(x, offset, enabled):
    if enabled:
        return setBit(x, offset)
    else:
        return clearBit(x, offset)


def readBit(x, offset):
    if testBit(x, offset):
        return True
    else:
        return False


def rearrange_filter_coeffs(b, a):
    """Rearrage coefficients from `a, b` to `c`."""
    return [b[0], a[1], a[2], b[1] / b[0], b[2] / b[0]]
