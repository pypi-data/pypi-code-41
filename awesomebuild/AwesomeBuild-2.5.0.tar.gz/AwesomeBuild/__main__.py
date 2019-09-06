#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import argparse
import json
import os

from .importer import importrules
from .JobManager import JobManager
from .RulesTree import RulesTree
from .Stats import Stats
from .StatusFile import StatusFile
from .Updater import Updater


def main():
    parser = argparse.ArgumentParser(
        description='Awesome build manager to replace Makefiles. '
        + 'It allows very fast building!')
    parser.add_argument('--dry-run', action='store_true',
                        help='Prevents all rules from running.')
    parser.add_argument('--updater', action='store_true',
                        help='Run Updater to fix deprecations.')
    parser.add_argument('--reset-stats', action='store_true',
                        help='Reset all statistics to default.')
    parser.add_argument('-j', dest='jobs', type=int,
                        help='Maximum number of jobs running in parallel. '
                        + 'Defaults to the number of cores available (' + str(os.cpu_count()) + '),')
    parser.add_argument('--config', default='awesomebuild.json',
                        help='default: awesomebuild.json')
    parser.add_argument('--status', default='awesomestatus.json',
                        help='Relative to project folder, '
                        + 'default: awesomestatus.json')
    parser.add_argument('--stats', nargs='?', const='',
                        help='Save statistics to given file name. Defaults to AwesomeStatistics.pdf.')
    parser.add_argument(
        'targets', nargs='*',
        help='defaults to the main rule defined in the config file'
    )
    args = parser.parse_args()

    run = True
    save = True

    configpath = os.path.abspath(
        (os.path.abspath(os.getcwd()) + '/'
         if args.config[0] != '/' else '') + args.config)

    if not os.path.isfile(configpath):
        raise FileNotFoundError('Config path invalid!')

    configdir = os.path.dirname(configpath)

    loaded = False
    updater_run = False
    while not loaded:
        with open(configpath) as json_file:
            data = json.load(json_file)
        if args.updater and not updater_run:
            Updater(data, configpath, configdir)
            updater_run = True
        else:
            loaded = True

    if 'rules' not in data:
        data['rules'] = {}

    data = importrules(data, configdir)

    targets = args.targets if len(args.targets) != 0 else [data['main']]

    if args.jobs is None:
        jobs = os.cpu_count()
    else:
        jobs = args.jobs

    statusfile = StatusFile(
        os.path.abspath(
            os.path.join(configdir, args.status)
        ),
        data
    )

    jobmanager = JobManager(jobs)
    stats = Stats(statusfile)
    rules = RulesTree(data, configdir, statusfile, jobmanager, stats)

    if args.reset_stats:
        run = False
        stats.reset()

    if args.dry_run:
        run = False
        save = False

    if run:
        for t in targets:
            rules[t].run()

    if args.stats is not None:
        stats.savePDF(
            os.path.join(
                configdir,
                args.stats
                if args.stats != ''
                else 'AwesomeStats.pdf'
            )
        )

    if save:
        stats.save()
        statusfile.save()


if __name__ == '__main__':
    main()
