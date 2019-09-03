import sys

def lssnaps():
    print("This is lssnaps")
    for index,arg in enumerate(sys.argv[2:]):
        print("{}:{}".format(index,arg))