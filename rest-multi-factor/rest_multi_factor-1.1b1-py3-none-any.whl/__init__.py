r"""
  _____  ______  _____ _______
 |  __ \|  ____|/ ____|__   __|
 | |__) | |__  | (___    | |
 |  _  /|  __|  \___ \   | |
 | | \ \| |____ ____) |  | |
 |_|  \_\______|_____/   |_|
  __  __       _ _   _   ______         _
 |  \/  |     | | | (_) |  ____|       | |
 | \  / |_   _| | |_ _  | |__ __ _  ___| |_ ___  _ __
 | |\/| | | | | | __| | |  __/ _` |/ __| __/ _ \| '__|
 | |  | | |_| | | |_| | | | | (_| | (__| || (_) | |
 |_|  |_|\__,_|_|\__|_| |_|  \__,_|\___|\__\___/|_|
"""

__title__ = "REST Multi Factor"
__author__ = "Joël Maatkamp"
__licence__ = "MIT"
__version__ = (__import__("rest_multi_factor.version", fromlist=["Version"])
               .Version(1, 1, 0, "beta", 1))

default_app_config = "rest_multi_factor.apps.RestMultiFactorConfig"
