# head---to get the first n lines of a file
# importing required in-built module
import os


def run(n, my_file):
    """ this function is called when head along with required argument are
    entered in PyShell"""
    try:
        with open(my_file) as f:
            first_n_lines = f.readlines()[0:-1*(int(n))]
    except Exception:
        from extern import extern_var
        print(extern_var.get('cant_find'))
    else:
        for d in first_n_lines:
            print(d, end="")
        print()
