#!/usr/bin/python3

import argparse
from land_sea_mask import createLSM
from cloud_type_identification import cloud_types


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-pf',
            '--precipColumn',
            type = str,
            required = True,
            help = 'Path to the 2C-PRECIP-COLUMN tar file or uncompressed directory',
            )
    parser.add_argument(
            '-gl',
            '--geoprofLidar',
            type = str,
            required = True,
            help = 'Path to the 2B-GEOPROF-LIDAR tar file or uncompressed directory',
            )
    parser.add_argument(
            '-r',
            '--reanalysis',
            type = str,
            required = True,
            help = 'Path to the reanalysis file that contains lts',
            )
    parser.add_argument(
            '-nc',
            '--netCDF',
            type = str,
            required = True,
            help = 'Path to the netCDF files to append to',
            )

    args = parser.parse_args()

    cldTypes = cloud_types.CloudType(args)
    cldTypes.run()

if __name__ == '__main__': main()
