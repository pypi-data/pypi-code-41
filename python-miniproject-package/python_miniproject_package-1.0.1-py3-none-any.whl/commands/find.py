import os


def run(file_path):
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
        print(os.path.join(current_directory , file_path))
    else:
        print("file or directory doesn't exit in current directories level")