"""
python GUI helpers
license:
GNU plublic license 3.0
contact developer os_sys for info or questions.
"""
#-----------imports-----------
from time import strftime
#-----------ERRORS-----------
class ERROR(Exception):
    """base error class"""
class GuiStartUpError(ERROR):
    """gui failed to start"""
class ExternalInterfaceError(ERROR):
    """an external interface interupted the program"""
#-----------variables-----------
succes = 'succes'
fail = 'failed'
#-----------functions-----------
def print_startup(*msg):
    import sys
    new = ''
    for i in msg:
        new += str(i) + ' '
    msg = new
    stamp = strftime("%Y-%m-%d %H:%M:%S")
    else:
        if __name__ == '__main__':
            print(f'startup info(python version: {sys.version}, time: {stamp})')
            print(msg,file=sys.stderr,flush=True)
