#!/usr/bin/env python

import argparse
import logging.config
import os


from reportIlluminaInterop.summary_stat import SummaryStat
from reportIlluminaInterop.settings import DEFAULT_LOG_DIR, PROJECT_NAME

logger = logging.getLogger(PROJECT_NAME + '.' + __name__)

def run(run_params):
    SummaryStat(run_params.input_folder).write_stats(run_params.input_folder, run_params.output_file)


def get_options():
    parser = argparse.ArgumentParser(description='Run the fastqcTaxonomy pipeline')
    parser.add_argument('--input-folder', type=str, required=True, help='Path to fastq folder')
    parser.add_argument('--output-file', type=str, required=True, help='Path to fastqc folder')
    parser.add_argument('--log-dir', type=str, required=False, default=DEFAULT_LOG_DIR,
                        help='Write log files to this directory')
    parser.add_argument('--logging_config', type=str, required=False,
                        help='Load logging configuration from this file (overrides default settings)')
    args = parser.parse_args()
    return args

def main():
    args = get_options()
    if args.logging_config:
        print("Loading logging configuration from file: %s" % args.logging_config)
        assert os.path.isfile(args.logging_config), 'Could not find logging configuration file %s' % args.logging_config
        logging.config.fileConfig(args.logging_config)
    else:
        from reportIlluminaInterop.logging_conf import add_run_log_handlers
        add_run_log_handlers(logs_dir=DEFAULT_LOG_DIR)
    run(args)

if __name__ == "__main__":
    main()
