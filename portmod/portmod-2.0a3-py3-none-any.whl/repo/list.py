# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3


def read_list(list):
    with open(list, mode="r") as list_file:
        return [line.strip() for line in list_file.read().splitlines()]
