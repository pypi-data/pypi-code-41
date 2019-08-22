import time
from datetime import datetime
import sys
import random
from north_c9.controller import C9Controller, C9Error
from tests import power, spreadsheet

SPREADSHEET = '1TwUHwPSHzjxD5xRhM4n7-YtBNbcsS3RVntzqjVrOMcs'
SHEET = 'Home and Move'

VELOCITY = 5000
ACCELERATION = 20000

C9_SERIAL = 'A505PD7K'

campaign = []
cycles = 0
errors = 0

positions = [
    [150, 150, 50],
    [250, 200, 150],
    [-200, 50, 250],
    [-250, -200, 200],
]

last_position = None


def random_position():
    global last_position
    while True:
        position = random.choice(positions)
        if position != last_position:
            last_position = position
            return position


def random_move():
    while True:
        try:
            c9.move_arm(*random_position(), velocity=VELOCITY, acceleration=ACCELERATION)
            return
        except C9Error as err:
            if err.error_number != C9Error.INVALID_POSITION:
                raise err


def connect():
    for i in range(0, 10):
        try:
            return C9Controller(device_serial=C9_SERIAL)
        except:
            time.sleep(1)

    raise Exception("Error Connecting after 10 attempts!")


#spreadsheet.append_row(SPREADSHEET, SHEET, [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), None, None])

#power.off()
#power.on()
c9 = connect()


while True:
    try:
        if cycles % 10 == 0:
            print()
            print(cycles, end=' ')

        c9.home(if_needed=False)

        for i in range(0, 2):
            random_move()

        cycles += 1
        print('.', end='')
        sys.stdout.flush()

    except Exception as err:
        errors += 1
        campaign.append(cycles)
        print()
        print('Error!', err)
        print('- cycles:', cycles)
        print('- errors:', errors)
        print('- campaign:', campaign)
        #spreadsheet.append_row(SPREADSHEET, SHEET, [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), cycles, getattr(err, 'error_number', None), str(err)])
        cycles = 0
        c9.disconnect()
        power.off()
        power.on()

        c9 = connect()