# mkdir--- to make a new directory
# importing required in-built module
import os


def run(args):
    """ this function is called when mkdir along with required argument are
    entered in PyShell"""
    try:
        # creating the required new directory
        os.mkdir(args)
    except FileExistsError:
        # handles exception
        from extern import extern_var
        print(extern_var.get('already_exists'))
    except FileNotFoundError:
        from extern import extern_var
        print(extern_var.get('invalid_path'))
