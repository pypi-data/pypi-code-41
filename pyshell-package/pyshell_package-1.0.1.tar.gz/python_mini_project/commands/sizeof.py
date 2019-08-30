# sizeof--- to get the size of directory
# importing required in-built module
import os


def run(path):
    """ this function is called when sizeof along with required argument are
    entered in PyShell"""
    try:
        ans = os.path.getsize(path)
    except FileNotFoundError:
        from extern import extern_var
        print(extern_var.get('doesnt_exist'))
    else:
        print(str(ans) + " bytes")
