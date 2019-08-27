from haohaninfo import GOrder

import platform
bit = platform.architecture()[0]
if(bit == '32bit'):
    from haohaninfo import version
else:
    from haohaninfo import version64
