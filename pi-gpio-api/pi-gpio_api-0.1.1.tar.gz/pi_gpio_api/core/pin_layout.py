GND_INFO = 'GND'
POWER_3V_INFO = '3V3 Power'
POWER_5V_INFO = '5V Power'
IO_INFO = 'IO'

POWER_3V_PINS = (1, 17)
POWER_5V_PINS = (2, 4)
GND_PINS = (6, 9, 14, 20, 25, 30, 34, 39)

IO_PINS = (3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26, 27,
           28, 29, 31, 32, 33, 35, 36, 37, 38, 40)
POWER_PINS = POWER_3V_PINS + POWER_5V_PINS + GND_PINS

ALL_PINS = POWER_PINS + IO_PINS


def pin_description(channel):
    group_pins = (POWER_3V_PINS, POWER_5V_PINS, GND_PINS, IO_PINS)
    info = (POWER_3V_INFO, POWER_5V_INFO, GND_INFO, IO_INFO)

    for pins, description in zip(group_pins, info):
        if channel in pins:
            return description

    raise AttributeError('Invalid channel')
