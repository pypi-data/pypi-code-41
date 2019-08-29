#ls
import os


def run(args=None):
    try:
        folder = os.getcwd()
        if args == None:
            for file in os.listdir(folder):
                print(file," ")
            print("\n")
            
        elif args == "-R":
            for(root,dirs,files) in os.walk(folder):
                print(root)
                print(dirs)
                print(files)
                print("\n")
        else:
            print('Wrong Arguments : type help followed by command')

    except KeyboardInterrupt as e:
        print(e)

