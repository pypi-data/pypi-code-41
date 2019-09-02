STATE = {True: 0x55,
         False: 0xFF}

COVER = dict()

COVER[0xA5] = dict(PROCEDURE={'ON': 0x01,  # SWITCH_ON
                              'STEP_UP': 0x01,
                              'OPEN': 0x01,
                              'INVERT': 0x02,  # SWITCH_INVERSION
                              'STOP': 0x02,
                              'OFF': 0x04,   # SWITCH_OFF
                              'STEP_DOWN': 0x04,
                              'CLOSE': 0x04,
                              'GLOBAL_ON': 0x06,
                              'GLOBAL_OFF': 0x07,
                              'SET_MODE': 0x0A,  # Откуда взялось?
                              'RESET_MODE': 0x0D,    # Откуда взялось?
                              },
                   EEPROM={'ADDRESS_NUMBER': 32,
                           'ADDRESS_SIZE': 4,
                           'START_SENSORS_ADDRESS': 0x00,

                           'STATE': 0xE0,
                           'HARDWARE_TYPE': 0xE8,
                           }
                   )

COVER[0xA9] = dict(PROCEDURE={'ON': 0x01,  # SWITCH_ON
                              'STEP_UP': 0x01,
                              'OPEN': 0x01,
                              'INVERT': 0x02,  # SWITCH_INVERSION
                              'STOP': 0x02,
                              'OFF': 0x04,   # SWITCH_OFF
                              'STEP_DOWN': 0x04,
                              'CLOSE': 0x04,
                              'GLOBAL_ON': 0x06,
                              'GLOBAL_OFF': 0x07,
                              'SET_MODE': 0x0A,  # Откуда взялось?
                              'RESET_MODE': 0x0D,    # Откуда взялось?
                              },
                   EEPROM={'ADDRESS_NUMBER': 32,
                           'ADDRESS_SIZE': 4,
                           'START_SENSORS_ADDRESS': 0x00,

                           'STATE': 0xE0,
                           'HARDWARE_TYPE': 0xE8,
                           }
                   )
