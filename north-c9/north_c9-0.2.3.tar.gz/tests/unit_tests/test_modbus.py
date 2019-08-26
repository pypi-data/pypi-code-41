import minimalmodbus

minimalmodbus.BAUDRATE = 38400
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = False
minimalmodbus.STOPBITS = 2

invalid_responses = 0

devices = [
    minimalmodbus.Instrument('COM19', 1),
    #minimalmodbus.Instrument('COM19', 2),
    #minimalmodbus.Instrument('COM19', 3),
    #minimalmodbus.Instrument('COM19', 4),
]


def request(device, method, *args):
    global invalid_responses
    for i in range(0, 10):
        try:
            return getattr(device, method)(*args)

        # retry the message if we run into a recoverable error (up to 9 times)
        except Exception as err:
            if str(err).startswith('Checksum error') or \
                    str(err).startswith('Too short') or \
                    str(err).startswith('No communication') or \
                    str(err).startswith('Wrong return slave'):
                if i >= 9:
                    raise err

                invalid_responses += 1
                print('Invalid responses: ', invalid_responses)
                # flush the input buffers so minimalmodbus doesn't go out of sync
                device.serial.reset_input_buffer()
            else:
                raise err


def home():
    for device in devices:
        # start homing (change state to 2)
        request(device, 'write_long', 6002, 2)

    # wait until the state of all devices is no longer 2
    while True:
        homing = False
        for device in devices:
            if request(device, 'read_long', 5000) == 2:
                homing = True

        if not homing:
            return


# attempt to home in a loop until we run into an error (after retrying the message 9 times)
while True:
    home()
