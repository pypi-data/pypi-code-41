STATE = {True: 0x55,
         False: 0xFF}

OPERATION_MODE = {'WHITE_STATIC': 1,
                  'COLOR_STATIC': 2,
                  'COLOR_DYNAMIC': 4,
                  'CONTROL_COMPUTER': 8,
                  'USER_1': 16,
                  'USER_2': 32,
                  'USER_3': 64,
                  'USER_4': 128,
                  }

RGB = dict()

RGB[0xA4] = dict(PROCEDURE={'SWITCH_ON': 0x01,
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

                         'STATE': 0xF6,
                         'ENABLE_SELECT_MODE': 0xF7,
                         'OPERATION_MODE': 0xF8,
                         'HARDWARE_TYPE': 0xE8,

                         'BRIGHTNESS_WHITE': 0xD0,
                         'BRIGHTNESS_STEP_WHITE': 0xD1,
                         'COLOR_POINT_STATIC': 0xD4,

                         'COLOR': 0xDC,             # RGB цвет
                         'BRIGHTNESS_RED': 0xDC,    # Яркость красного канала
                         'BRIGHTNESS_GREEN': 0xDD,  # Яркость зеленого канала
                         'BRIGHTNESS_BLUE': 0xDE,   # Яркость синего канала

                         'FIRMWARE_VERSION': 0xF0,
                         'TIME_RELAY_OFF': 0xF5,
                         'DIMMING_SPEED': 0xF7,
                         'DIMMING_STEP': 0xF9,
                         }
                 )


