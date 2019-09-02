STATE = {True: 0x55,
         False: 0xFF}

BRIGHTNESS = dict(MIN=0x00,
                  MAX=70)

DIMMING_STEP = dict(MIN=1,
                    MAX=20)

RELAY = dict()

RELAY[0xA5] = dict(PROCEDURE={'SWITCH_ON': 0x01,
                              'STEP_UP': 0x01,
                              'SWITCH_INVERSION': 0x02,
                              'SWITCH_OFF': 0x04,
                              'STEP_DOWN': 0x04,
                              'GLOBAL_ON': 0x06,
                              'GLOBAL_OFF': 0x07,
                              'SET_MODE': 0x0A,
                              'RESET_MODE': 0x0D,
                              },
                   EEPROM={'ADDRESS_NUMBER': 32,
                           'ADDRESS_SIZE': 4,
                           'START_SENSORS_ADDRESS': 0x00,

                           'STATE': 0xE0,
                           'BRIGHTNESS_LEVEL': 0xE1,
                           'BRIGHTNESS_LEVEL_COMFORT': 0xE2,
                           'HARDWARE_TYPE': 0xE8,

                           'FIRMWARE_VERSION': 0xF0,
                           'TIME_RELAY_OFF': 0xF5,
                           'DIMMING_SPEED': 0xF7,
                           'DIMMING_STEP': 0xF9,
                           }
                   )

RELAY[0xA9] = dict(PROCEDURE={'SWITCH_ON': 0x01,
                              'STEP_UP': 0x01,
                              'SWITCH_INVERSION': 0x02,
                              'SWITCH_OFF': 0x04,
                              'STEP_DOWN': 0x04,
                              'GLOBAL_ON': 0x06,
                              'GLOBAL_OFF': 0x07,
                              'SET_MODE': 0x0A,
                              'RESET_MODE': 0x0D,
                              },
                   EEPROM={'ADDRESS_NUMBER': 32,
                           'ADDRESS_SIZE': 4,
                           'START_SENSORS_ADDRESS': 0x00,

                           'STATE': 0xE0,
                           'BRIGHTNESS_LEVEL': 0xE1,
                           'BRIGHTNESS_LEVEL_COMFORT': 0xE2,
                           'HARDWARE_TYPE': 0xE8,

                           'FIRMWARE_VERSION': 0xF0,
                           'TIME_RELAY_OFF': 0xF5,
                           'DIMMING_SPEED': 0xF7,
                           'DIMMING_STEP': 0xF9,
                           }
                   )
