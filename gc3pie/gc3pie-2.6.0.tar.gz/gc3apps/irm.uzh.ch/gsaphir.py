#!/usr/bin/env python
#
#   gsaphir.py -- Front-end script for submitting multiple saphir jobs.
#
#   last modified: 28.09.2017 by Akos Dobay
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Front-end script for submitting multiple `saphir` jobs.
It uses the generic `gc3libs.cmdline.SessionBasedScript` framework.

See the output of ``gsaphir --help`` for program usage instructions.
"""

__version__ = 'development version 1.0 (SVN $Revision$)'
__author__ = 'Akos Dobay'
__docformat__ = 'reStructuredText'


import os
import glob
import decimal
import itertools
import tarfile
import tempfile

import gc3libs
from gc3libs import Application, Run
from gc3libs.cmdline import SessionBasedScript, executable_file, existing_file
from gc3libs.workflow import ChunkedParameterSweep
from gc3libs.utils import irange, parse_range, write_contents

if __name__ == '__main__':
    import gsaphir
    gsaphir.GSaphirScript().run()


class GSaphirApplication(Application):
    """
    Class wrapping the execution of a single `saphir` program.
    """

    application_name = "gsaphir"

    def __init__(self,
                 executable,
                 search_radius,
                 exclusion_zone,
                 scaling_factor,
                 intensity_threshold,
                 input_file,
                 input_image,
                 **extra_args):

        extra_args.setdefault('requested_cores', 1)

        self.executable = executable
        self.search_radius = search_radius
        self.exclusion_zone = exclusion_zone
        self.scaling_factor = scaling_factor
        self.intensity_threshold = intensity_threshold
        self.input_file = input_file
        self.input_image = input_image

        extra_args.setdefault('jobname',
                              "GSaphir:%i:%i:%i:%f:%s"
                              % (search_radius, exclusion_zone, scaling_factor, intensity_threshold,
                                 os.path.basename(input_image)))

        if 'output_dir' in extra_args:
            extra_args['output_dir'] = os.path.join(
                os.path.dirname(extra_args['output_dir']),
                extra_args['jobname'])

        executable_script = """#!/bin/sh

# exit immediately on error
set -e

echo "==> Working directory contents:"
ls -l

# Create data directory

mkdir -pv data

# Run the script

echo "==> Running 'saphir' ..."
./{saphir} -r {search_radius} -e {exclusion_zone} -c {scaling_factor} -t {intensity_threshold} -f {input_file} -s {input_image} -D data

# Compress all output files

#gzip data/*.txt
#gzip data/*.png

""".format(
    saphir=os.path.basename(executable),
    search_radius=int(search_radius),
    exclusion_zone=int(exclusion_zone),
    scaling_factor=int(scaling_factor),
    intensity_threshold=float(intensity_threshold),
    input_file=os.path.basename(input_file),
    input_image=os.path.basename(input_image),
)
        try:
            (fd, self.tmp_filename) = tempfile.mkstemp(prefix='gc3pie-gsaphir_')
            write_contents(self.tmp_filename, executable_script)
            os.chmod(self.tmp_filename, 0o755)
        except Exception as ex:
            gc3libs.log.error(
                "Error creating execution script: %s: %s",
                type(ex), ex)
            raise

        input_files = {
            # local abs path : remote file name
            executable: os.path.basename(executable),
            self.tmp_filename: 'gsaphir.sh',
            input_file: os.path.basename(input_file),
            input_image: os.path.basename(input_image),
        }

        output_files = {
            # download this remote file ...
            'data/dimension.txt':
                # ...into this local one
                'dimension.txt',
            # download this remote file ...
            # ??? how is the output image named?
            os.path.join('data', os.path.basename(self.input_image)):
                # ...into this local one
                ('er_{er}_sr_{sr}_sf_{sf}_it_{it}_{image}'
                 .format(
                     er=self.exclusion_zone,
                     sr=self.search_radius,
                     sf=self.scaling_factor,
                     it=(int((1 - self.intensity_threshold) * 100)),
                     image=os.path.basename(self.input_image)))
        }

        Application.__init__(
            self,
            ['./gsaphir.sh'],
            inputs=input_files,
            outputs=output_files,
            stdout="gsaphir.out",
            stderr="gsaphir.err",
            **extra_args)

    def terminated(self):
        """
        Remove temporary script file
        """
        try:
            os.remove(self.tmp_filename)
        except Exception as ex:
            # non-fatal error: log and ignore
            gc3libs.log.warning(
                "Failed removing temporary file %s: %s: %s ",
                self.tmp_filename, type(ex), ex)


class GSaphirTaskCollection(ChunkedParameterSweep):

    def __init__(self,
                 executable,
                 search_radius_range,
                 exclusion_zone_range,
                 scaling_factor_range,
                 intensity_threshold_range,
                 input_file,
                 input_image,
                 chunk_size,
                 **extra_args):

        self.executable = executable
        self.extra_args = extra_args
        self.input_file = input_file
        self.input_image = input_image

        self.combinations = list(
            itertools.product(
                irange(*search_radius_range),
                irange(*exclusion_zone_range),
                irange(*scaling_factor_range),
                irange(*intensity_threshold_range),
            )
        )

        ChunkedParameterSweep.__init__(
            self,
            0, # min value
            len(self.combinations), # max value, has to be at least 2
            1, # step
            chunk_size,
            **extra_args
        )

    def new_task(self, param, **extra):
        sr, ez, sf, it = self.combinations[param]
        return GSaphirApplication(
            self.executable,
            sr, ez, sf, it, self.input_file, self.input_image,
            **self.extra_args)


class GSaphirScript(SessionBasedScript):
    """
    Run multiple instances of `saphir` with the combination of
    supplied parameters.
    """
    version = __version__
    application_name = 'gsaphir'

    def setup_options(self):
        self.add_param("-a", "--search-radius", required=True,
                       help="In the form N[:END:STEP]. If only `N` is "
                       "supplied, will use only that value, otherwise "
                       "will use all the values in the range from `N` "
                       "to `END` (exclusive) using `STEP` increments")

        self.add_param("-e", "--exclusion-zone", required=True,
                       help="In the form N[:END:STEP]. If only `N` is "
                        "supplied, will use only that value, otherwise "
                        "will use all the values in the range from `N` "
                        "to `END` (exclusive) using `STEP` increments")

        self.add_param("-b", "--scaling-factor", required=True,
                       help="In the form N[:END:STEP]. If only `N` is "
                            "supplied, will use only that value, otherwise "
                            "will use all the values in the range from `N` "
                            "to `END` (exclusive) using `STEP` increments")

        self.add_param("-t", "--intensity-threshold", required=True,
                       help="In the form N[:END:STEP]. If only `N` is "
                            "supplied, will use only that value, otherwise "
                            "will use all the values in the range from `N` "
                            "to `END` (exclusive) using `STEP` increments")

        self.add_param("-f", "--source-file", type=existing_file,
                       help="Read the original dimension file")

        self.add_param("-I", "--source-image", type=existing_file,
                       help="Read the image source")

        self.add_param("-x", "--executable", type=executable_file,
                       default='saphir', metavar='FILE',
                       help="Path to the saphir executable.")

    def parse_args(self):
        if self.params.search_radius:
            self.params.search_radius_range = parse_range(self.params.search_radius)

        if self.params.exclusion_zone:
            self.params.exclusion_zone_range = parse_range(self.params.exclusion_zone)

        if self.params.scaling_factor:
            self.params.scaling_factor_range = parse_range(self.params.scaling_factor)

        if self.params.intensity_threshold:
            self.params.intensity_threshold_range = parse_range(self.params.intensity_threshold)

        self.params.executable = os.path.abspath(self.params.executable)

    def new_tasks(self, extra):
        return [
            GSaphirTaskCollection(
                self.params.executable,
                self.params.search_radius_range,
                self.params.exclusion_zone_range,
                self.params.scaling_factor_range,
                self.params.intensity_threshold_range,
                self.params.source_file,
                self.params.source_image,
                1000, # FIXME! make an option, do not hard-code
                **extra.copy()
            )
        ]
