# ls---- listing files inside a directory
# importing required in-built module
import os


def run(args=None):
    """ this function is called when ls along with required argument are
    entered in PyShell"""
    try:
        # for non - recursive call
        folder = os.getcwd()
        if args is None:
            for file in os.listdir(folder):
                print(file, " ")
                
        # for recursive call
        elif args is "-R" or args is "--recursive":
            for(root, dirs, files) in os.walk(folder):
                print(root)
                print(dirs)
                print(files)  
                   
        else:
            from extern import extern_var
            print(extern_var.get('wrong_arg'))

    # handles exception
    except KeyboardInterrupt as e:
        print(e)
