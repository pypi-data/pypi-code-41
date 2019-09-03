# To use custom settings copy this sample to settings_local.py or customize it at ~/.nqontrol.py
# The settings_local.py will overwrite the user config file.

#################### Local configuration ####################
# Use 0 to enable a dummy device. Otherwise use the channel number
DEVICES_LIST = [0]  # The 0 is reserved to mock device for testing!
# DEVICES_LIST = [1]

# SETTINGS_FILE = 'test.json'
# CREATE_SETTINGS_BACKUP = False
# BACKUP_SUBSTRING = "%Y-%m-%d_%H-%M-%S"

# You can do two things, either first create the SERVO_NAMES object and then add names for specific deviceNumber...
# SERVO_NAMES = {}
# SERVO_NAMES[1] = {
#     1: 'Cavity',
#     3: 'Mode Cleaner',
# }
# ... or just set them all in one:
# SERVO_NAMES = {
#     0: {
#         1: 'Cavity',
#         3: 'Mode Cleaner',
#     },
#     1: {
#         4: 'Resonator',
#         5: 'Temp',
#     }
# }
# When initialized, the ServoDevice will check whether names are available for its deviceNumber.

# DEBUG = True

# NUMBER_OF_SERVOS = 8  # only for one device currently
# NUMBER_OF_MONITORS = 8  # same

# LOG_LEVEL = 'INFO'
