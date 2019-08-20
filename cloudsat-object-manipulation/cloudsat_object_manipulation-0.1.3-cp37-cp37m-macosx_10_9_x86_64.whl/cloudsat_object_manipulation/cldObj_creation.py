#!/usr/bin/python3

import argparse
from cloudsat_object_manipulation import objCreate
from sys import exit

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
            '-o',
            '--output',
            help = 'Path to the output directory',
            type = str,
            required = True
            )
    parser.add_argument(
            '-d',
            '--dataset',
            type = str,
            required = True,
            help = 'dataset to analyze',
            )
    parser.add_argument(
            '-iv',
            '--idVariables',
            nargs = '+',
            default = [],
            type = lambda x : x.split(','),
            required = True,
            help = 'list of variables to use for identification'
            )
    parser.add_argument(
            '-s',
            '--scale',
            action = 'store_true',
            help = 'flag used to unpack data',
            )
    parser.add_argument(
            '-m',
            '--mask',
            action = 'store_true',
            help = 'flag used to mask data',
            )
    parser.add_argument(
            '-v',
            '--verbose',
            action = 'store_true',
            help = 'verbose flag (print files being converted',
            )
    parser.add_argument(
            '-ovr',
            '--overwrite',
            action = 'store_true',
            help = 'if output file exists overwrite it',
            )
            
    args = parser.parse_args()
    
    runObjectCreate = objCreate.cloudSatObjects(args)
    runObjectCreate.run()

if __name__ == '__main__': main()
