import argparse
from rh_match import rhMatch

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-gl',
            '--geoprofLidar',
            type = str,
            required = True,
            help = 'Path to the 2B-GEOPROF-LIDAR tar file or uncompressed directory',
            )
    parser.add_argument(
            '-rh',
            '--relativeHumidity',
            type = str,
            required = True,
            help = 'Path to the reanalysis file that contains relative humidity',
            )
    parser.add_argument(
            '-geo',
            '--geopotential',
            type = str,
            required = True,
            help = 'Path to the reanalysis file that contains geopotential',
            )
    parser.add_argument(
            '-nc',
            '--netCDF',
            type = str,
            required = True,
            help = 'Path to the netCDF files to append to',
            )

    args = parser.parse_args()

    rhObj = rhMatch.MatchRH(args.geoprofLidar,args.relativeHumidity,args.geopotential,args.netCDF)
    rhObj.run()

if __name__ == '__main__': main()
