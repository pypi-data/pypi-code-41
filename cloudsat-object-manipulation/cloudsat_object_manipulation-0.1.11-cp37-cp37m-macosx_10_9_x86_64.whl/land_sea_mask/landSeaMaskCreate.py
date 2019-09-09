#!/usr/bin/python3

import argparse
from land_sea_mask import createLSM


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-i',
            '--input',
            type = str,
            required = True,
            help = 'Path to the input tar file or uncompressed directory',
            )
    parser.add_argument(
            '-nc',
            '--netCDF',
            type = str,
            required = True,
            help = 'Path to the netCDF files to append to',
            )

    args = parser.parse_args()
    lsmOBJ = createLSM.LSM(args)
    lsmOBJ.run()

#if __name__ == '__main__': main()
