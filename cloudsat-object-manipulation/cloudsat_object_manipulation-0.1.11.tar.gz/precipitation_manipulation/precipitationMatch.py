#!/usr/bin/python3

import argparse
from precipitation_manipulation import precipAnalysis


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-rr',
            '--rainRate',
            type = str,
            required = True,
            help = 'Path to the input tar file or uncompressed directory of the rain rate product (2C-RAIN-PROFILE)',
            )
    parser.add_argument(
            '-pf',
            '--precipFlag',
            type = str,
            required = True,
            help = 'Path to the input tar file or uncompressed directory of the precipitation flag product (2C-PRECIP-COLUMN)',
            )
    parser.add_argument(
            '-nc',
            '--netCDF',
            type = str,
            required = True,
            help = 'Path to the netCDF files to append to',
            )

    args = parser.parse_args()
    precipOBJ = precipAnalysis.PrecipMatch(args)
    precipOBJ.run()

if __name__ == '__main__': main()
