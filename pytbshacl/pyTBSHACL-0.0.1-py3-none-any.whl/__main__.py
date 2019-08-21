"""

"""
import os
import sys
import argparse
import logging
import tbshacl
import tbshacl.report
import tempfile
import rdflib
import json

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--log_level',
                        action='count',
                        default=0,
                        help='Set logging level, multiples for more detailed.')
    parser.add_argument("-d","--datafile",
                        default=None,
                        help="Path to data file in turtle format")
    parser.add_argument("-df", "--data_format", default="turtle",
                        help="Format of data_file (turtle)")
    parser.add_argument("-s","--shapefile",
                        default=None,
                        help="Optional path to shape file in turtle format")
    parser.add_argument("-of","--out_format",default="turtle",
                        help="Output format: turtle (default) | text | json")
    args = parser.parse_args()
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = levels[min(len(levels) - 1, args.log_level)]
    logging.basicConfig(level=log_level,
                        format="%(asctime)s %(levelname)s %(message)s")
    if args.datafile is None:
        logging.error("Datafile is required.")
        return 1
    data_file = args.datafile
    temp_name = None
    if args.data_format.lower() != "turtle":
        # Create a temporary file to hold the converted RDF
        fdest, temp_name = tempfile.mkstemp(suffix=".ttl")
        os.close(fdest)
        g = rdflib.Graph()
        g.parse(source=args.datafile, format=args.data_format)
        g.serialize(temp_name, format="turtle")
        data_file = temp_name
        logging.info("Wrote turtle to " + data_file)
        with open(data_file, "r") as ftmp:
            logging.debug(ftmp.read())
    resout, reserr = tbshacl.tbShaclValidate(data_file, shape_file=args.shapefile)
    if not temp_name is None:
        os.unlink(temp_name)
    if resout is None:
        return 2
    sys.stderr.write(reserr.decode())
    out_format = args.out_format.lower()
    if out_format == "turtle":
        sys.stdout.write(resout.decode())
        return 0
    results = tbshacl.report.reportDictFromGraph(resout, shape_file=args.shapefile)
    if out_format == "json":
        print(json.dumps(results, indent=2))
        return 0
    print(tbshacl.report.reportDictToText(results))
    return 0

if __name__ == "__main__":
    sys.exit(main())