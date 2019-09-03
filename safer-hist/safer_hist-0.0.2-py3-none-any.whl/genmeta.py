import sys

def genmeta():
    print("This is genmeta")
    for index,arg in enumerate(sys.argv[2:]):
        print("{}:{}".format(index,arg))