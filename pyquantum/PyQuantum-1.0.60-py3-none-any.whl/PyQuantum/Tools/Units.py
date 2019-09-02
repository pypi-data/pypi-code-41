from PyQuantum.Tools.Assert import *

Hz = 1         # 1 Гц
KHz = 10 ** 3  # 1 KГц
MHz = 10 ** 6  # 1 МГц
GHz = 10 ** 9  # 1 ГГц

ms = 1e-3  # 1 мс
mks = 1e-6  # 1 мкс
ns = 1e-9  # 1 мкс


# ---------------------------------------------------------------------------------------------------------------------
def time_unit(time):
    Assert(time >= 1e-9, 'time < 1 ns', FILE(), LINE())

    if time >= 1:
        unit = 's'
    elif time >= 1e-3:
        unit = 'ms'
    elif time >= 1e-6:
        unit = 'mks'
    elif time >= 1e-9:
        unit = 'ns'

    return unit
# ---------------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
def frequency_unit(frequency):
    Assert(frequency >= 1, 'frequency < 1 Hz', FILE(), LINE())

    if frequency >= 1e9:
        unit = 'GHz'
    elif frequency >= 1e6:
        unit = 'MHz'
    elif frequency >= 1e3:
        unit = 'KHz'
    else:
        unit = 'Hz'

    return unit
# ---------------------------------------------------------------------------------------------------------------------
