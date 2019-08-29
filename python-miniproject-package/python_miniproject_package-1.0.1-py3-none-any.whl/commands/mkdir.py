#mkdir

import os 


def run(args):
    try:
        os.mkdir(args)
    except FileExistsError:
        print("directory  that is to be created already exists")
    except FileNotFoundError:
        print("the specified path is invalid")