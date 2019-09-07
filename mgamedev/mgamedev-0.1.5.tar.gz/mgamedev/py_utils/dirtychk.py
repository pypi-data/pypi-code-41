#encoding:utf8 

import os 
import string

DIRTY_WORDS = ["FUCK", "FXXK"]
output = []

def iter_path(tpath):
    print("Chking the path-->>", tpath)
    for filename in os.listdir(tpath):
        fileobj = os.path.join(tpath, filename)
        if os.path.isdir(fileobj):
            iter_path(fileobj)
        else:
            for dword in DIRTY_WORDS:
                if string.find(filename.upper(), dword) != -1:
                    output.append(filename)
            

iter_path(os.getcwd())
print (output, "--->>output")