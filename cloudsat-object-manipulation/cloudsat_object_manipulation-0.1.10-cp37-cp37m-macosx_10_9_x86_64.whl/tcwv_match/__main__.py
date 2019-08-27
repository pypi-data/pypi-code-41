import argparse
from tcwv_match import tcwvID

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

    tcwvObj = tcwvID.MatchTCWV(args.reanalysis,args.geoprofLidar,args.netCDF)
    tcwvObj.run()

if __name__ == '__main__': main()
