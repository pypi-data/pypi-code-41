# grep---to get the first n lines of a file
# importing required in-built module
import os
from doctest import testmod


def run(n, pattern, src):
    """ this function is called when grep along with required argument are
    entered in PyShell"""
    file_handle = open(src, 'r')
    all_lines = file_handle.readlines()
    file_handle.close()
    count = 0
    for line in all_lines:
        count = count+1
        if line.find(pattern) > -1:
            print(os.path.basename(src)+":"+str(count)+":"+" " + line, end="")
    print()
