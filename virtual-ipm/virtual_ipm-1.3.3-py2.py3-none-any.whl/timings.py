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

from __future__ import absolute_import, unicode_literals

from collections import defaultdict
import json
import time

cpu_time_per_component = defaultdict(float)
cpu_time_elapsed = 0.


def measure_cpu_time(method):
    def wrapper(self, *args, **kwargs):
        global cpu_time_elapsed

        before = time.clock()
        result = method(self, *args, **kwargs)
        after = time.clock()
        cpu_time_per_component[(self, method)] += (after - before)
        cpu_time_elapsed = after
        return result
    return wrapper


def compute_percentages():
    return {k: v / cpu_time_elapsed * 100. for k, v in cpu_time_per_component.items()}


def compute_formatted_percentages():
    return {k: '%2.1f' % v for k, v in compute_percentages().items()}


def dump_statistics_to_file(filepath):
    def format_key(key):
        return '%s.%s' % (key[0].__class__.__name__, key[1].__name__)

    stats = {
        'cpu times': {format_key(k): v for k, v in dict(cpu_time_per_component).items()},
        'percentages': {format_key(k): v for k, v in compute_percentages().items()},
    }

    with open(filepath, str('w')) as fp:
        json.dump(stats, fp, indent=4)
