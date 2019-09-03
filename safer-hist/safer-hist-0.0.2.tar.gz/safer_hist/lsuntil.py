import sys

def lsuntil():
    print("This is lsuntil")
    for index,arg in enumerate(sys.argv[2:]):
        print("{}:{}".format(index,arg))