# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import sys
import re
from distutils.util import strtobool
from portmod.colour import bright, lgreen, lred


def prompt_bool(question):
    sys.stdout.write(
        "{} [{}/{}]: ".format(question, bright(lgreen("Yes")), bright(lred("No")))
    )
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write(
                "Please respond with '{}' or '{}': ".format(
                    bright(lgreen("Yes")), bright(lred("No"))
                )
            )


def parse_num_list(string):
    if string == "":
        return list()

    m = re.match(r"(\d+)(?:-(\d+))?$", string)
    if not m:
        raise TypeError(
            "'{}' is not a range of number. Expected forms like '0-5' or '2'.".format(
                string
            )
        )
    start = m.group(1)
    end = m.group(2) or start
    return list(range(int(start, 10), int(end, 10) + 1))


def prompt_num_multi(question, max_val):
    print("{}: ".format(question))
    while True:
        try:
            result = [y for x in input().split(",") for y in parse_num_list(x)]
            if next(filter(lambda x: x > max_val or x < 0, result), None):
                print(
                    "Please ensure that the numbers are between 0 and {}".format(
                        max_val
                    )
                )
            else:
                return result
        except ValueError:
            print(
                "Please respond using a-b to indicate a range and a,b "
                "to indicate individual numbers: "
            )


def prompt_num(question, max_val, cancel=False):
    print("{}: ".format(question))
    while True:
        try:
            result = int(input())
            if result > max_val or result < 0:
                if result == -1 and cancel:
                    return result

                print(
                    "Please ensure that the number is between 0 and {}".format(max_val)
                )
            else:
                return result
        except ValueError:
            print("Please enter a number between 0 and {}".format(max_val))
