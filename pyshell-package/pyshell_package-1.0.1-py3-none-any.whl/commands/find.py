# find---to find the file inside a directory
# importing required in-built module
import os


def run(file_path):
    """ this function is called when find along with required argument
    are entered in PyShell"""
    pwd = os.getcwd()
    if_contains = 'false'
    for (root, dirs, files) in os.walk(pwd):
        if(os.path.isdir(file_path)):
            if dirs.__contains__(file_path):
                print("directory exists")
                current_directory = root
                if_contains = 'true'
                break
            else:
                continue
        elif os.path.isfile(file_path):
            if files.__contains__(file_path):
                print("file exists")
                current_directory = root
                if_contains = 'true'
                break
            else:
                continue
    if(if_contains == 'true'):
        print(os.path.join(current_directory, file_path))
    else:
        from extern import extern_var
        print(extern_var.get('doesnt_exist'))
