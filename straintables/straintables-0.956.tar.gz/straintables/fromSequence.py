#!/bin/python

import os
import argparse
import pandas as pd


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", dest="WorkingDirectory")

    options = parser.parse_args()

    return options


def main():
    options = parse_arguments()

    MatchedRegionsPath = os.path.join(options.WorkingDirectory, "MatchedRegions.csv")
    if os.path.isfile(MatchedRegionsPath):
        MatchedRegions = pd.read_csv(MatchedRegionsPath)
    else:
        MatchedPrimersData = []
        files = [
            f for f in os.listdir(options.WorkingDirectory)
            if f.endswith(".fasta")
        ]



if __name__ == "__main__":
    main()
