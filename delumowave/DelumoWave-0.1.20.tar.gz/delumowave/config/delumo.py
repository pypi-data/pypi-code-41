# General eeprom addresses for settings
EEPROM_HARDWARE_TYPE = 0xE8
EEPROM_FIRMWARE_VERSION = 0xF0
EEPROM_SIZE = 256


# Devices types
DEVICE = dict(COMPUTER=0x00,
              GIDROLOCK=0x01,
              DELUMO=0x02,
              THERMOREGULATOR=0x03)

# Commands
COMMAND = dict(WRITE_EEPROM=0x01,
               READ_EEPROM=0x02,
               RESPONSE=0x03,
               EXECUTE_PROCEDURE=0x07)

HARDWARE_TYPE = dict(RELAY=0x5E,
                     DIMMER=0x5D,
                     RGB=0x5C)