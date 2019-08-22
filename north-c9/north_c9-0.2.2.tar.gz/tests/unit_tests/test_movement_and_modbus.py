import time
from datetime import datetime
import sys
import random
from north_c9.controller import C9Controller, C9Error
from tests import power, spreadsheet, modbus

SPREADSHEET = '1TwUHwPSHzjxD5xRhM4n7-YtBNbcsS3RVntzqjVrOMcs'
SHEET = 'Move and Current'
MESSAGES_SHEET = 'Move and Current (Messages)'

C9_SERIAL = 'A505PD7K'
COM_SERIAL = 'FT2FT5C1'

VELOCITY = 5000
ACCELERATION = 20000

campaign = []
cycles = 0
errors = 0

positions = [
    [150, 150],
    [250, 200],
    [-200, 50],
    [-250, -200],
]

last_position = None

test_id = str(time.time())

#monitor = modbus.ModbusMonitor(test_id, device_serial=COM_SERIAL)
#monitor.start()

def random_position():
    global last_position
    z = random.randrange(100, 250)
    x_invert = random.choice([1, -1])
    while True:
        position = random.choice(positions)
        if position != last_position:
            last_position = position
            return [position[0] * x_invert, position[1], z]


def random_move():
    while True:
        try:
            c9.move_arm(*random_position(), velocity=VELOCITY, acceleration=ACCELERATION)
            return
        except C9Error as err:
            if err.error_number != C9Error.INVALID_POSITION:
                raise err


def find_modbus_timeout_axis():
    for i in range(0, 4):
        try:
            c9.axis_current(i)
        except C9Error:
            return i


def connect():
    for i in range(0, 10):
        try:
            return C9Controller(device_serial=C9_SERIAL)
        except:
            time.sleep(1)

    raise Exception("Error Connecting after 10 attempts!")


def save_cycle_data(recovered):
    axis = find_modbus_timeout_axis()
    row = [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), test_id, axis, cycles, recovered, getattr(err, 'error_number', None), str(err)]
    spreadsheet.append_row(SPREADSHEET, SHEET, row)


#def save_message_data():
#    rows = [message.row() for message in monitor.get_messages()]
#    spreadsheet.append_rows(SPREADSHEET, MESSAGES_SHEET, rows)


#power.off()
#power.on()
c9 = connect()
c9.home()

while True:
    try:
        if cycles % 100 == 0:
            print()
            print(cycles, end=' ')

        #monitor.cycle = cycles
        random_move()
        for i in range(0, 4):
            c9.axis_current(i)

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

        recovered = False

        if isinstance(err, C9Error) and err.error_number == C9Error.MODBUS_TIMEOUT:
            time.sleep(10)
            try:
                c9.axis_positions(0, 1, 2, 3, test=True)
                # if we've recovered from the timeout error, move on
                recovered = True
            except:
                pass

        save_cycle_data(recovered)
        #save_message_data()

        if not recovered:
            cycles = 0
            test_id = str(time.time())
            c9.disconnect()
            power.off()
            power.on()

            c9 = connect()
            c9.home()