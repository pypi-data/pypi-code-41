IN = 0
OUT = 1
I2C = 2
SPI = 3
HARD_PWM = 4
SERIAL = 5
UNKNOWN = 6
BOARD = 0
HIGH = True
LOW = False
RPI_INFO = {'board': 'Not a RPi'}


def setmode(brd):
    pass


def cleanup(channel=0):
    pass


def setup(channel, fcn):
    pass


def input(channel):
    return 0


def output(channel, state):
    pass
