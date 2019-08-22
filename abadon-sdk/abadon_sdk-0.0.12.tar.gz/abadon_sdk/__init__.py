import sys

if sys.version_info >= (3,):
    from abadon_sdk.abadon_sdk import *
    from abadon_sdk.env import *
else:
    from abadon_sdk import *
    from env import *
