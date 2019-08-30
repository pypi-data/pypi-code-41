# rm--- to remove files
# importing required in-built module
import os


def run(dir, args=None):
    """ this function is called when rm along with required arguments are
    entered in PyShell"""
    # for non-recursive call
    if args is None:
        if(os.path.isfile(dir)):
            os.unlink(dir)
    # for recursive call
    elif os.path.exists(dir) and args == "-r":
        for the_file in os.listdir(dir):
            file_path = os.path.join(dir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                else:
                    run(file_path, "-r")
                os.rmdir(dir)
            # handles exception, if occurred
            except Exception as e:
                print(e)
    # takes care of invalid cases
    elif args is not None and args != "-r":
        from extern import extern_var
        print(extern_var.get('wrong_arg'))
