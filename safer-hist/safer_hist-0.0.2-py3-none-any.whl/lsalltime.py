import sys

def lsalltime():
    print("This is lsalltime")
    for index,arg in enumerate(sys.argv[2:]):
        print("{}:{}".format(index,arg))