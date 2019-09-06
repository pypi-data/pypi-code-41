#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2017  The IPMSim collaboration <http://ipmsim.gitlab.io/IPMSim>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import logging
import pprint
import sys

from anna import load_from_file
import pyhocon

import virtual_ipm
from virtual_ipm.control.threading import SimulationThread
import virtual_ipm.log as log
import virtual_ipm.timings as timings


parser = argparse.ArgumentParser()

parser.add_argument(
    'config',
    help='File path pointing to a configuration file.'
)
parser.add_argument(
    '--version',
    action='version',
    version=virtual_ipm.__version__
)
parser.add_argument(
    '--quiet-console',
    action='store_true',
    help='Use this switch to suppress all console output.'
)
parser.add_argument(
    '--console-log-level',
    choices=('debug', 'info', 'warning', 'error', 'critical'),
    nargs='?',
    const='info',
    default='info',
    type=str,
    help='Set the logging level to one of the levels available in the Python logging library.'
)
parser.add_argument(
    '--log-to-file',
    help='In addition to the console log entries will be stored in the specified file.'
)
parser.add_argument(
    '--file-log-level',
    choices=('debug', 'info', 'warning', 'error', 'critical'),
    nargs='?',
    const='debug',
    default='debug',
    type=str,
    help='The level for file logging can be set independently from the console.'
)
parser.add_argument(
    '--timing-stats-to-file',
    help='The timing (performance) statistics will be written to the specified file.'
)


def main():
    args = parser.parse_args()

    if not args.quiet_console:
        log.to_console(level=getattr(logging, args.console_log_level.upper()))

    if args.log_to_file:
        log.to_file(args.log_to_file, level=getattr(logging, args.file_log_level.upper()))

    def create_configuration_from_args():
        # Default filename for the setup configuration.
        boot_file = 'boot.conf'

        setup_config = pyhocon.ConfigFactory.from_dict({
            name: getattr(args, name)
            for name in filter(
                lambda name: getattr(args, name) is not None,
                ['config']
            )
        })

        try:
            # Specifiers have precedence over parameters stored in the boot file.
            setup_config = setup_config.with_fallback(pyhocon.ConfigFactory.parse_file(boot_file))
        except IOError:
            log.root_logger.debug('Setup configuration file "%s" not found.', boot_file)

        return load_from_file(setup_config['config'])

    thread = SimulationThread()
    thread.setup(create_configuration_from_args())
    thread.run()

    log.root_logger.debug('----- Timing Statistics -----')
    log.root_logger.debug('CPU time:')
    log.root_logger.debug(pprint.pformat(dict(timings.cpu_time_per_component)))
    log.root_logger.debug('Percentages:')
    log.root_logger.debug(pprint.pformat(timings.compute_formatted_percentages()))

    if args.timing_stats_to_file:
        timings.dump_statistics_to_file(args.timing_stats_to_file)

    return 0


if __name__ == '__main__':
    sys.exit(main())
