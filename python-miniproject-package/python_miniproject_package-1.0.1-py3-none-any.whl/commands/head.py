#head
import os


def run(n, my_file):
    try:
        with open(my_file) as f:
            first_n_lines = f.readlines()[0:-1*(int(n))]
    except:
        print("Error: can\'t find file or read data")
    else:
        for d in first_n_lines:
            print(d)