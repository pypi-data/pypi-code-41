# -*- encoding: utf-8 -*-

# hints about entry points from
# https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/

import logging
import json
import configparser

from argparse import ArgumentParser

from woohoo_pdns import pdns


def main():
    # TODO: consider using 'click' or 'docopt' instead of ArgumentParser
    # https://realpython.com/comparing-python-command-line-parsing-libraries-argparse-docopt-click/
    # http://docopt.org/
    # http://click.pocoo.org/5/
    parser = ArgumentParser(prog="pdns", description="CLI for woohoo pDNS.")

    parser.add_argument("-f",
                        "--config-file",
                        help="The config file to use, must contain the connection string for the "
                             "database, e.g. 'conn_str = sqlite:///test.db' in a section called '[DB]'")

    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument("-q", "--quiet", action="store_true", help="be quiet (only output critical messages)")
    log_group.add_argument("-v", "--verbose", action="store_true", help="be verbose")
    log_group.add_argument("-d", "--debug", action="store_true", help="be as verbose as you can")

    # parser.add_argument("-S", "--no-syslog", action="store_true", help="disable logging to syslog")

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="available subcommands",
        help='see help for respective sub-command')

    parser_l = subparsers.add_parser('load', help='load data into the pDNS database')
    parser_l.set_defaults(func=load_data)  # have 'load_data' called
    parser_l.add_argument("file",
                          metavar="FILE",
                          type=str,
                          help="complete, absolute path to file/directory to read (load)")
    parser_l.add_argument("-j",
                          "--json",
                          action="store_true",
                          help="the input file contains JSON data (e.g. previously exported data)")
    parser_l.add_argument("-b",
                          "--batch-size",
                          metavar="BATCH_SIZE",
                          type=int, default=10000,
                          help="max. number of records to load at once")
    parser_l.add_argument("-p",
                          "--pattern",
                          metavar="GLOB_PATTERN",
                          type=str,
                          help="a glob pattern to apply when loading all files in a directory")
    parser_l.add_argument("--no-rename", action="store_false", dest="rename", default=True,
                          help="do not rename files after processing")

    parser_e = subparsers.add_parser('export', help='export data to a JSON file')
    parser_e.set_defaults(func=export_data)  # have 'export_data' called
    parser_e.add_argument("file", metavar="FILE", type=str, help="complete, absolute path to file to write (export)")

    parser_q = subparsers.add_parser('query', help='query the database (returns JSON)')
    parser_q.set_defaults(func=query)  # have 'query' called
    parser_q.add_argument("query", metavar="QUERY", type=str, help="the query, use '*' as wildcard")
    parser_q.add_argument("--rdata", action="store_true", default=False, help="run an rdata query (always true for IP)")

    cfg = parser.parse_args()

    if cfg:
        if cfg.config_file:
            config_f = configparser.ConfigParser()
            config_f.read(cfg.config_file)
            cfg.conn_str = config_f["DB"]["conn_str"]
            try:
                cfg.loader = config_f["LOAD"]["loader_class"]
            except KeyError:
                cfg.loader = "woohoo_pdns.load.SilkFileImporter"
            try:
                cfg.data_timezone = config_f["LOAD"]["data_timezone"]
            except KeyError:
                cfg.data_timezone = "UTC"
        else:
            cfg.conn_str = "sqlite:///demo.db"
            cfg.loader = "woohoo_pdns.load.SilkFileImporter"
            cfg.data_timezone = "UTC"
        if cfg.quiet:
            logging.basicConfig(level=logging.ERROR)
        elif cfg.verbose:
            logging.basicConfig(level=logging.INFO)
        elif cfg.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING)

        # if not cfg.no_syslog:
        #     handler = logging.handlers.SysLogHandler(address='/dev/log')

        # call the correct function
        # https://docs.python.org/3.6/library/argparse.html#sub-commands
        # try/except required because of bug
        # https://stackoverflow.com/a/54161510/254868
        # without it we have an exception when no subcommand and no command line flag are provided
        try:
            cfg.func(cfg)
        except AttributeError:
            parser.print_help()
            parser.exit()


def load_data(cfg):
    logger = logging.getLogger(__name__)
    in_file = cfg.file
    logger.info("Started loading file/directory '{}'".format(in_file))
    d = _connect(cfg.conn_str)
    logger.debug("Assuming new data is in timezone '{}' if I have to guess".format(cfg.data_timezone))
    loader_cfg = {
        "file_pattern": cfg.pattern,
        "rename": cfg.rename
    }
    d.load(
        in_file,
        batch_size=cfg.batch_size,
        cfg=loader_cfg,
        data_timezone=cfg.data_timezone,
        loader=cfg.loader)
    logger.warning("Done loading file/directory '{}'".format(in_file))


def export_data(cfg):
    logger = logging.getLogger(__name__)
    out_file = cfg.file
    logger.info("Started export to file '{}'".format(out_file))
    d = _connect(cfg.conn_str)
    with open(out_file, "w") as fh:
        for r in d.records:
            fh.write(json.dumps(r.to_jsonable()))
            fh.write("\n")


def query(cfg):
    d = _connect(cfg.conn_str)
    r = d.query(cfg.query, cfg.rdata)
    for rec in r:
        print(json.dumps(rec.to_jsonable(), indent=4, default=str, sort_keys=True))


def most_recent(cfg):
    d = _connect(cfg.conn_str)
    r = d.most_recent
    print(json.dumps(r.to_jsonable(), indent=4, default=str, sort_keys=True))


def _connect(conn_str):
    return pdns.Database(conn_str)


if __name__ == "__main__":
    main()
