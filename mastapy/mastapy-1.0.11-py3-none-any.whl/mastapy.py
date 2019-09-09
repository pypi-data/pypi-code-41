import clr

MASTA_PROPERTIES = dict()

def masta_property(func=None, name='', *, description='', symbol='', measurement=''):
    '''Decorator method for creating MASTA properties in Python

    Keyword arguments:
    -- func: The function that the decorator is wrapping
    -- name: The name of the property displayed in Masta
    -- description: The description of what the property does (optional)
    -- symbol: The symbol for the property displayed in Masta (optional)
    -- measurement: Unit the property displayed in, in Masta (optional)
    '''
    def decorator_masta_property(func):
        import inspect
        x = inspect.getfullargspec(func)
        if 'return' in x.annotations:
            returns = x.annotations['return']
        else:
            returns = None
        MASTA_PROPERTIES[func.__name__] = func, x.annotations[x.args[0]], name, description, symbol, measurement, returns
        return func

    return decorator_masta_property if func is None else decorator_masta_property(func)


def init(path_to_dll_folder):
    '''Initialises the Python to MASTA API interop

    Keyword arguments:
    -- path_to_dll_folder: Path to your MASTA folder that
                           includes the MastaAPI.dll file.
                           This should be a RAW STRING.
    '''
    import os
    import errno

    full_path = os.path.join(path_to_dll_folder, 'MastaAPI.dll')
    if not os.path.exists(full_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), full_path)

    clr.AddReference(full_path)
    from SMT.MastaAPI import UtilityMethods
    UtilityMethods.InitialiseApiAccess(path_to_dll_folder)


def start_debugging(host='localhost', port=5678, timeout=10):
    '''Initialises Python debugging

    Keyword arguments:
    -- host: Debug server ip address
    -- port: Debug server port
    -- timeout: How long the program will wait for a debugger attachment. 
                Execution will pause until the debugger has been attached.
    '''
    import ptvsd
    ptvsd.enable_attach(address=(host, port), redirect_output=True)
    ptvsd.wait_for_attach(timeout)
    print('Waiting for debugger attach')