#tail

import os


def run(n, my_file):
    try:
        with open(my_file) as f:
            last_n_lines = f.readlines()[int(n):]
    except:
        print("Error: can't find file or read data")
    else:
        for d in last_n_lines:
            print(d)