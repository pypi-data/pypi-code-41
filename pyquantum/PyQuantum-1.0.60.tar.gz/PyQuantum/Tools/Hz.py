def to_Hz(value, precision=3):
    if value >= 1e9:
        value_str = str(round(value / 1e9, precision)) + " GHz"
    elif value >= 1e6:
        value_str = str(round(value / 1e6, precision)) + " MHz"
    elif value >= 1e3:
        value_str = str(round(value / 1e3, precision)) + " KHz"
    else:
        value_str = str(round(value, precision)) + " Hz"

    return value_str


def value_str_v(value, precision=3):
    if value >= 1e9:
        value_str = str(round(value / 1e9, precision))
    elif value >= 1e6:
        value_str = str(round(value / 1e6, precision))
    elif value >= 1e3:
        value_str = str(round(value / 1e3, precision))
    else:
        value_str = str(round(value, precision))

    return value_str
