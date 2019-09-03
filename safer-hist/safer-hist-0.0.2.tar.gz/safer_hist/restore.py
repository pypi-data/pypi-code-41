import sys

def restore():
    print("This is restore")
    for index,arg in enumerate(sys.argv[2:]):
        print("{}:{}".format(index,arg))