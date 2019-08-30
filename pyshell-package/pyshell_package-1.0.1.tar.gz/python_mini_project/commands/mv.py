# mv--- to move files
# importing required in-built module
import os


def run(src, dest):
    """ this function is called when mv along with required argument are
    entered in PyShell"""
    try:
        src_file = os.path.basename(src)
        if os.path.isdir(dest):
            dest = os.path.join(dest, src_file)
        if os.path.exists(dest):
            os.unlink(dest)
        os.rename(src, dest)
    except Exception as e:
        print(e)
