import os


def run(dir,args=None):
    if args == None:
        if(os.path.isfile(dir)):
            os.unlink(dir)
    elif os.path.exists(dir) and args == "-r":
        for the_file in os.listdir(dir):
            file_path = os.path.join(dir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                else:
                    run(file_path, "-r")
                os.rmdir(dir)
            except Exception as e:
                print(e)
    elif args != None and args != "-r":
          print('Wrong Arguments : type help followed by command')
            