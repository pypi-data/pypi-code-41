from qaviton_processes import pip as p


class PIP:
    """wrapper around pip"""
    def __init__(pip): pip.version = pip('--version')
    def __call__(pip, *args): return p(*args)
    def install(pip, *args): return pip('install', *args)
    def uninstall(pip, *args): return pip('uninstall', *args, '-y')
    def freeze(pip, filename, *args): return pip('freeze', '>', filename, *args)
    def exist(pip, package):
        try: pip(f'show {package}'); return True
        except: return


pip = PIP()
