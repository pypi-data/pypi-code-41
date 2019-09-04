#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of xanity.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import numpy as np
from fnmatch import fnmatch
import re
import shutil
import argparse
import pandas as pd

from .constants import RELATIVE_PATHS, DIRNAMES
from .common import Alias, pickle_load, CommandSet, XanityCommand, confirm
from .constants import EXPERIMENT_LOG_HEADER
from .constants import RUN_DIR_REGEX

XANITY_ROOT = None


def get_root():
    global XANITY_ROOT
    from . import xanity as _xanity
    if _xanity.project_root:
        XANITY_ROOT = _xanity.project_root


def get_n_bytes(path):
    return int(subprocess.check_output([
        'du', '-bs', path
    ]).decode().split('\t')[0])


def try_load(file):
    try:
        return pickle_load(file)
    except:
        print('problem loading {}'.format(file))
        return None


def isa_rundir(path):
    if path is None:
        return False
    return True if re.match(RUN_DIR_REGEX, os.path.split(path)[1]) else False


def split_rundir(rundir):
    if os.sep in rundir:
        rundir = os.path.split(rundir)[-1]

    match = re.match(RUN_DIR_REGEX, rundir)

    if match:
        return match.groups()
    else:
        return None


def split_runid(runid):
    return re.match(RUN_DIR_REGEX, runid).groups()


def runid2path(runid):
    allruns = list_all_rundirs()
    return [path for path in allruns if fnmatch(split_rundir(path)[0], runid)]


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def score_exp_dir(path):
    score = 0
    c2 = os.listdir(path)

    for ff in c2:

        filepath = os.path.join(path, ff)

        # point for log and another if it's big
        if fnmatch(ff, '*xanity*.log'):
            score += 1
            if os.stat(filepath).st_size > 1000:
                score += 1

        if os.path.isdir(filepath):

            if ff == 'xanity_variables':
                # it's not a subexp, it's xanity storage
                score += len(os.listdir(filepath))

            else:
                # it's a subexp
                score += score_exp_dir(filepath)

    return score


# def find_all_runs(experiment_name=None):
#     allruns = get_rundirs(experiment=experiment_name)
#     myruns = []
#
#     if not experiment_name:
#         return allruns
#
#     for rd in allruns:
#         c0 = os.listdir(rd)
#         for d in c0:
#             if d == experiment_name:
#                 # check for subdirs
#                 t1 = os.path.join(rd, d)
#                 c1 = os.listdir(t1)
#                 for dd in c1:
#                     if fnmatch(dd, experiment_name + '_*'):
#                         # its a subdir... add it
#                         myruns.append(os.path.join(t1, dd))
#                         continue
#                 myruns.append(t1)
#
#     return myruns

def resolve_data_spec(pathstring):
    matches = set()

    if pathstring in list_all_experiments():
        ## an entire experiment was requested
        matches.update(get_rundirs(experiments=pathstring, include_saved=True))

    elif re.match(RUN_DIR_REGEX, pathstring):
        # a specific run was requested:
        matches.update(get_rundirs(regex=pathstring, include_saved=True))

    else:
        # a portion of a run_id was requested:
        alldata = list_all_rundirs()
        for item in alldata:
            if re.match(pathstring, item):
                matches.update(item)

    return list(matches)


def list_all_experiments(debug=False, not_debug=False, saved=False, not_saved=False):
    included = []
    get_root()
    if not XANITY_ROOT:
         return []

    else:
        return [e_name for e_name in os.listdir(os.path.join(XANITY_ROOT, RELATIVE_PATHS.run_data)) \
                if os.path.isdir(os.path.join(XANITY_ROOT, RELATIVE_PATHS.run_data, e_name))]


def list_all_rundirs(saved_only=False, not_saved_only=False):
    if not saved_only and not not_saved_only:
        saved_only = True
        not_saved_only = True

    datapaths = []
    get_root()

    if not_saved_only:
        datapaths.extend([os.path.join(XANITY_ROOT, RELATIVE_PATHS.run_data, name) for name in list_all_experiments()])
    if saved_only:
        datapaths.extend(os.path.join(XANITY_ROOT, RELATIVE_PATHS.saved_data))


kn_selectors = {
    'saved': ('saved', 'save'),
    'not_saved': ('not-saved', 'not_saved'),
    'debug': ('debug', 'debugging'),
    'not_debug': ('not-debug', 'not-debugging', 'not_debug', 'not_debugging'),
    'complete': ('complete', 'done'),
    'incomplete': ('incomplete', 'incomp', 'running'),
    'failed': ('failed', 'unsuccessful'),
    'successful': ('successful', 'succeeded', 'good', 'not-failed', 'not_failed'),
    'all': ('all', ),
    'experiments': list_all_experiments(),
}


def parse_selectors(selectors):
    result = {}

    # if not selectors:
    #     selectors = ''

    if isinstance(selectors, str):
        selectors = selectors.split(' ')

    assert (all([isinstance(item, str) and ' ' not in item for item in selectors]))

    def is_known(string):
        for sel, aliases in kn_selectors.items():
            if string in aliases:
                return True
        return False

    for sel in selectors:
        if not is_known(sel):
            raise ValueError('didn\'t recognize selector \'{}\''.format(sel))

    for key, val in kn_selectors.items():
        if key == 'experiments':
            result[key] = [item for item in selectors if item in list_all_experiments()]
        else:
            result[key] = True if set(val).intersection(selectors) else False

    return result


def select_rundirs(
        experiments=None,
        regex=None,
        fnmatch_str=None,
        saved=False, not_saved=False,
        debug=False, not_debug=False,
        complete=False, incomplete=False,
        failed=False, successful=False,
        all=False):

    get_root()

    rundirs, scores, sizes, logsizes, success, iscomplete = scan_data(
        experiments=experiments,
        sort='alpha', order='ascending', normalize=False, include_incomplete=True,
        include_saved=True)

    selected = set(range(len(rundirs)))

    if not all:
        if incomplete:
            selected.difference_update([i for i, val in enumerate(iscomplete) if val == True])

        if complete:
            selected.difference_update([i for i, val in enumerate(iscomplete) if val == False])

        if failed:
            selected.difference_update([i for i, val in enumerate(success) if val == True])

        if successful:
            selected.difference_update([i for i, val in enumerate(success) if val == False])

        if debug:
            selected.difference_update([i for i, val in enumerate(rundirs) if 'debug' not in split_rundir(val)[0]])

        if not_debug:
            selected.difference_update([i for i, val in enumerate(rundirs) if 'debug' in split_rundir(val)[0]])

        if saved:
            selected.difference_update([i for i, path in enumerate(rundirs)
                                        if os.path.join(XANITY_ROOT, RELATIVE_PATHS.run_data) in path])

        if not_saved:
            selected.difference_update([i for i, path in enumerate(rundirs)
                                        if os.path.join(XANITY_ROOT, RELATIVE_PATHS.saved_data) in path])

        if regex:
            selected.difference_update([i for i, path in enumerate(rundirs)
                                        if not re.match(regex, split_rundir(path)[0])])

        if fnmatch_str:
            selected.difference_update([i for i, path in enumerate(rundirs)
                                        if not fnmatch(split_rundir(path)[0], fnmatch_str)])

    return [d for i, d in enumerate(rundirs) if i in selected]


def get_rundirs(experiments=None,
                include_saved=True, include_not_saved=True,
                include_debug=True, include_not_debug=True,
                fnmatch_str=None,
                regex=None):

    datapaths = []
    results = []
    get_root()

    if experiments:
        if isinstance(experiments, str):
            experiments = list(experiments.split(' '))
    else:
        experiments = list_all_experiments()

    if include_not_saved:
        datapaths.extend([os.path.join(XANITY_ROOT, RELATIVE_PATHS.run_data, name) for name in experiments])

    if include_saved:
        datapaths.extend(os.path.join(XANITY_ROOT, RELATIVE_PATHS.saved_data))

    datapaths = [pp for pp in datapaths if os.path.isdir(pp)]
    all_runs = [os.path.join(datapath, dd) for datapath in datapaths for dd in os.listdir(datapath)]

    for run in all_runs:
        deets = split_rundir(run)
        if not deets:
            continue
        if regex and not re.match(regex, run):
            continue
        if fnmatch_str and not fnmatch(run, fnmatch_str):
            continue
        if not include_debug and 'debug' in deets[0]:
            continue
        if not include_not_debug and 'debug' not in deets[0]:
            continue
        results.append(run)

    results.sort()
    return results


def scan_logs(experiment, regex, numeric=False):
    logfiles = []
    results = []
    allruns = get_rundirs(experiments=experiment)

    for root in allruns:
        if any([fnmatch(item, experiment + '_*') for item in os.listdir(root)]) and os.path.isdir(
                os.path.join(root, experiment)):
            # it's a subdir
            subdirs = [item for item in os.listdir(root) if fnmatch(item, experiment + '_*')]
            logfiles.extend([os.path.join(root, sd, experiment + DIRNAMES.EXP_LOG_SUFFIX) for sd in subdirs])
        else:
            # it's not a subdir
            logfiles.extend([os.path.join(root, experiment + DIRNAMES.EXP_LOG_SUFFIX)])

    for log in logfiles:
        if os.path.isfile(log):
            with open(log, 'r') as f:
                for line_no, line in enumerate(f.readlines()):
                    m = re.match(string=line, pattern=regex)
                    if m:
                        if numeric:
                            try:
                                results.append(np.array([float(item) for item in m.groups()]))
                            except:
                                print('could not perform numeric conversion on item in {}::{}'.format(log, line_no))
                                results.append(m.groups())
                        else:
                            results.append(m.groups())

    return results if not numeric else np.array(results, dtype='float32')


def scan_data(rundirs=None,
              experiments=None,
              regex=None,
              fnmatch_str=None,
              sort='alpha',
              top=0,
              order='increasing',
              normalize=False,
              include_saved=True, include_incomplete=True, include_debug=True,
              print_results=False,
              headings=20):

    if not rundirs:
        rundirs = get_rundirs(experiments=experiments,
                              include_saved=include_saved,
                              include_debug=include_debug,
                              fnmatch_str=fnmatch_str,
                              regex=regex)

    names = [0] * len(rundirs)
    scores = [0] * len(rundirs)
    sizes = [0] * len(rundirs)
    success = [True] * len(rundirs)
    complete = [True] * len(rundirs)

    if not rundirs:
        return [], scores, sizes, [], success, complete

    for i, d in enumerate(rundirs):
        name = os.path.split(d)[-1]
        names[i] = name
        score = 0

        if not os.path.isdir(d) or not re.match(RUN_DIR_REGEX, name):
            continue

        if os.path.isfile(os.path.join(d, 'xanity_info', 'unsuccessful')):
            success[i] = False
            complete[i] = True

        elif os.path.isfile(os.path.join(d, 'xanity_info', 'successful')):
            success[i] = True
            complete[i] = True

        elif os.path.isfile(os.path.join(d, 'xanity_info', 'xanity_panic.dill')) \
                or os.path.isfile(os.path.join(d, 'xanity_panic.dill')):
            success[i] = False
            complete[i] = True

        else:
            success[i] = None
            complete[i] = False

        if not '-debug' in name:
            score += 1

        # look at the top-level structure
        c1 = os.listdir(d)

        score += len(c1) - 2  # two dirs created by xanity

        # get its size
        size = get_n_bytes(d)
        sizes[i] = size

        for sd, dirs, fs in os.walk(os.path.join(d)):
            for ff in fs:
                score += 1

        scores[i] = score

    if include_incomplete:
        scores = np.array(scores)
        sizes = np.array(sizes)
        logsizes = np.log(sizes)
        success = np.array(success, dtype=bool)
        complete = np.array(complete, dtype=bool)

    else:
        rundirs = [d for i, d in enumerate(rundirs) if complete[i]]
        scores = np.array(scores)[complete]
        sizes = np.array(sizes)[complete]
        logsizes = np.log(sizes)  # complete already selected
        success = np.array(success, dtype=bool)[complete]
        complete = np.array(complete, dtype=bool)[complete]

    # corrections
    # scores = scores-scores.min()

    n_scores = 100 * scores / np.median(scores)
    n_sizes = 100 * sizes / np.median(sizes)
    n_logsizes = 100 * logsizes / np.median(logsizes)

    composite_scores = n_scores + n_logsizes
    n_composite_scores = 100 * composite_scores / np.median(composite_scores)

    if normalize:
        scores = n_scores
        sizes = n_sizes
        logsizes = n_logsizes
        composite_scores = n_composite_scores

    if sort == 'composite_score':
        ranks = np.argsort(composite_scores)
    elif sort == 'alpha':
        ranks = np.argsort(names)
    elif sort == 'size':
        ranks = np.argsort(sizes)
    elif sort == 'score':
        ranks = np.argsort(scores)
    else:
        raise ValueError("I didn't understand that sorting request")

    if sort:
        if order in ['decreasing', 'descending']:
            ranks = ranks[::-1]
        elif order in ['increasing', 'ascending']:
            pass
        else:
            raise ValueError("didn't recognize that sort order request")

    if isinstance(top, int) and top > 0:
        ranks = ranks[:top]

    if print_results:

        for i, index in enumerate(ranks):
            if headings and headings > 0 and not i % headings:
                print("#############################################################################################")
                print("#            run                                score     size      logsize    composite    #")
                print("#############################################################################################")
                #   2019-03-05-202910_experiment1_73        0.22      0.2 %      0.2 %      0.4 %

            if not normalize:
                print("   {:40s}    {:5.1f}    {:8s}    {:5.1f}    {:5.1f} %".format(
                    names[index], scores[index], sizeof_fmt(sizes[index]), logsizes[index], composite_scores[index]
                ))
            else:
                print("   {:40s}    {:5.1f} %    {:5.1f} %    {:5.1f} %    {:5.1f} %".format(
                    names[index], scores[index], sizes[index], logsizes[index], composite_scores[index]
                ))

    return [rundirs[i] for i in ranks], scores[ranks], sizes[ranks], logsizes[ranks], success[ranks], complete[ranks]


def summarize_data(rundirs=None, log=True, top=5, cols=2, exp_summary=True):

    get_root()

    rundirs, scores, sizes, logsizes, success, complete = scan_data(
        rundirs=rundirs, sort='size', order='increasing', normalize=False, include_saved=True, include_incomplete=True)
    exps = [item for item in os.listdir(os.path.join(XANITY_ROOT, 'data/runs')) if
            os.path.isdir(os.path.join(XANITY_ROOT, 'data', 'runs', item))]
    datacount = len(sizes)
    top = datacount if top > datacount else top
    n_rows = int(np.ceil(float(top) / cols))
    inds_by_col = np.array_split(np.arange(top), cols)

    if datacount == 0:
        print('looks like you haven\'t created any data yet')
        return

    print('Total runs of data:     {}\n'.format(datacount))

    if exp_summary:
        print('By experiment:')
        print('\n'.join(['    {}: {}  ({} successful)'.format(
            exp,
            len(os.listdir(os.path.join(XANITY_ROOT, 'data', 'runs', exp))),
            len([True for i, rd in enumerate(rundirs) if split_rundir(rd)[1] == exp and success[i]])
        ) for exp in exps]))
        print("")

    print("smallest {}:".format(top))
    for i in range(n_rows):
        rowtext = '  '
        for j, col in enumerate(inds_by_col):
            if i >= len(col):
                continue
            rowtext += '{:<35s}  {:>10s},    '.format(os.path.split(rundirs[col[i]])[-1], sizeof_fmt(sizes[col[i]]))
        print(rowtext)
    print("")

    print("largest {}:".format(top))
    for i in range(n_rows):
        rowtext = '  '
        for j, col in enumerate(inds_by_col):
            if i >= len(col):
                continue
            rowtext += '{:<35s}  {:>10s},    '.format(os.path.split(rundirs[-1 - col[i]])[-1],
                                                      sizeof_fmt(sizes[-1 - col[i]]))
        print(rowtext)
    print("")

    print("Log Histogram (pct of total):\n")
    print_histogram(sizes)


# def remove_broken_links(verbose=False):
#     def test_and_clean(path):
#         if path == '/home/bjmuld/work/volterraPY/data/runs/by_experiment/de/2019-02-28-143205-debug':
#             fake = True
#         try:
#             _ = os.stat(path)
#         except OSError as e:
#             if e.errno == 2:
#                 print('cleaning up {}'.format(os.path.join(path))) if verbose else None
#                 os.remove(path)
#         return
#
#     all_exps = get_rundirs(include_saved=False, by_experiment=True)
#     for exp in all_exps:
#
#         test_and_clean(exp)
#
#         for root, sdirs, files in os.walk(exp):
#
#             for sd in sdirs:
#                 test_and_clean(os.path.join(root, sd))
#             for ff in files:
#                 test_and_clean(os.path.join(root, ff))


def purge(experiments, **kwargs):
    if experiments == 'all':
        experiments = list_all_experiments()

    elif isinstance(experiments, str):
        experiments = [experiments]

    for experiment in experiments:
        dirs = inspect_experiment(experiment, long=True, include_saved=False)
        if dirs:
            try:
                if not confirm('You are about to delete all data associated with \'{}\'.\n'
                               'are you sure about that??'.format(experiment),
                               default_response=False):
                    return
            except KeyboardInterrupt:
                print('')
                return

            for path in dirs:
                shutil.rmtree(path)
            # remove_broken_links()


def prune(rundirs=None,
          metric='size', threshold=0.01, unit='fraction',
          print_sizes=False, human_readable=False,
          full_path=False, full_path_only=False, count_only=False,
          delete=False, include_saved=False,
          print_scores=False):
    acceptable_metrics = ['size', 'logsize', 'score', 'composite_score']
    acceptable_units = ['percent', 'unit', 'fraction', 'bytes', 'B', 'b', 'bits', 'byte', 'bit']

    if unit in ['B', 'bytes']:
        unit = 'bytes'
    elif unit in ['b', 'bits']:
        unit = 'bits'

    if isinstance(threshold, str):

        if 'b' in threshold:
            unit = 'bits'
            threshold = threshold.rstrip('b')

            if 'k' in threshold.lower():
                threshold = float(threshold.lower().split('k')[0]) * (10 ** 3)
            elif 'm' in threshold.lower():
                threshold = float(threshold.lower().split('m')[0]) * (10 ** 6)
            elif 'g' in threshold.lower():
                threshold = float(threshold.lower().split('g')[0]) * (10 ** 9)
            elif 't' in threshold.lower():
                threshold = float(threshold.lower().split('t')[0]) * (10 ** 12)

        elif 'B' in threshold:
            unit = 'bytes'
            threshold = threshold.rstrip('B')

            if 'k' in threshold.lower():
                threshold = float(threshold.lower().split('k')[0]) * (2 ** 10)
            elif 'm' in threshold.lower():
                threshold = float(threshold.lower().split('m')[0]) * (2 ** 20)
            elif 'g' in threshold.lower():
                threshold = float(threshold.lower().split('g')[0]) * (2 ** 30)
            elif 't' in threshold.lower():
                threshold = float(threshold.lower().split('t')[0]) * (2 ** 40)

        elif '%' in threshold:
            unit = 'percent'
            threshold = float(threshold.strip('%'))

        elif '/' in threshold:
            unit = 'fraction'
            threshold = float(threshold.split('/')[0]) / float(threshold.split('/')[1])

        elif '.' in threshold:
            if not unit:
                unit = 'fraction'
            threshold = float(threshold)

        else:
            if not unit:
                unit = 'bytes'
            threshold = int(threshold)

    if not isinstance(threshold, (int, float)):
        print('must specify threshold as a scalar quantity')
        return
    if not isinstance(metric, str) or metric not in acceptable_metrics:
        print('must specify metric ({})'.format(acceptable_metrics))
        return
    if not isinstance(unit, str) or unit not in acceptable_units:
        print('must specify unit ({})'.format(acceptable_units))
        return

    rundirs, scores, sizes, logsizes, success, complete = scan_data(
        rundirs=rundirs,
        sort='size', order='ascending', normalize=False,
        include_saved=include_saved)

    if metric == 'size':
        prunescores = sizes
    elif metric == 'logsize':
        prunescores = logsizes
    elif metric == 'score':
        prunescores = scores
    elif metric == 'logscore':
        prunescores = np.log(scores)

    if unit == 'percent':
        prunescores = prunescores.astype(float) / np.max(prunescores) * 100.0
    elif unit == 'fraction':
        prunescores = prunescores.astype(float) / np.max(prunescores)
    elif unit == 'bits':
        prunescores = 8 * sizes

    del_upto = np.searchsorted(prunescores, threshold, side='left')

    if count_only:
        print('these params would prune {} runs out of {}'.format(del_upto, len(scores)))
        return del_upto

    if delete:
        try:
            if not confirm('you are about to delete {} runs worth of precious data. are you sure?'.format(del_upto),
                           default_response=False):
                return
        except KeyboardInterrupt:
            print('')
            return

        rmfailpaths = []

        def log_failed_dirs(function, path, excinfo):
            rmfailpaths.append(path)

        for path in rundirs[:del_upto]:
            shutil.rmtree(path, ignore_errors=False, onerror=log_failed_dirs)
            if path not in rmfailpaths:
                print('removed {}'.format(path))

    else:
        col = []
        if full_path or full_path_only:
            col.append(rundirs[:del_upto])
        else:
            col.append([row.split(os.sep)[-1] for row in rundirs[:del_upto]])

        print('## threshold = {} {}'.format(threshold, '%' if unit == 'fraction' else unit))

        if print_sizes and not full_path_only:
            if human_readable:
                col.append([sizeof_fmt(row) for row in sizes[:del_upto]])
            else:
                col.append([row for row in sizes[:del_upto]])

        if print_scores:
            if unit == 'percent':
                col.append(['{:5.1f}%'.format(row) for row in prunescores[:del_upto]])
            else:
                col.append(['{:5.1g}'.format(row) for row in prunescores[:del_upto]])
        for row in zip(*col):
            print(' '.join(['{:<}'] * len(col)).format(*row))


def print_histogram(values, height=10, width=74, barwidth=2, ticks=4, log=True):
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    values = values.ravel()

    bins = int(width / barwidth)
    tick_inds = list((np.arange(ticks).astype(float) / np.array((ticks - 1)).astype(float) * bins).astype(int))
    tick_space = int(width / (ticks + 1))

    hist, edges = np.histogram(values, bins=bins, density=True)
    if log:
        hist, _ = np.histogram(np.log(values), bins=bins, density=True)

    hist = (height * hist.astype(float) / hist.max().astype(float)).astype(int)

    histarray = []

    for i, col in enumerate(hist):
        histarray.append(np.concatenate([
            np.zeros(height - hist[i]),
            np.ones(hist[i] + 1)
        ]))

    for i, row in enumerate(np.stack(histarray).T):
        print('  {}'.format(''.join([''.join(['#'] * barwidth) if x else ''.join([' '] * barwidth) for x in row])))

    print(''.join([" "] * (tick_space)).join(['{:8s}'.format(sizeof_fmt(entry)) for entry in edges[tick_inds]]))
    print('\n')


def inspect_variable(variable_name, long=False):
    locations = find_xanity_variable(variable_name)
    if locations:
        print(' {:>25}    {:<}'.format(
            'xanity variable:',
            variable_name
        ))
        print('')
        print(' {:>25}    {:<}'.format(
            'experiments:',
            len(locations)
        ))

        sizes = np.array([get_n_bytes(item) for item in locations])
        print(' {:>25}    {:<}'.format(
            'median size:',
            sizeof_fmt(np.median(sizes))
        ))
        print(' {:>25}    {:<}'.format(
            'min, max size:',
            '{},  {}'.format(sizeof_fmt(sizes.min()), sizeof_fmt(sizes.max()))
        ))

        print('')
        print('  histogram of sizes:\n')
        print_histogram(sizes)


def inspect_experiment(experiment, variable_name=None, long=False, include_saved=True):
    paths = get_rundirs(experiments=experiment, include_saved=include_saved)

    print(' {:>25}    {:<}'.format(
        'experiment:',
        experiment
    ))

    print(' {:>25}    {:<}'.format(
        'total starts:',
        len(paths)
    ))

    affiliated_variables = set()
    for run in paths:
        affiliated_variables.update(set(tuple(list_xanity_variables(path=run))))

    print(' {:>25}    {:<}'.format(
        'affiliated variables:',
        str(list(affiliated_variables))
    ))

    return paths


def inspect_run(runid, variable_name=None, print_head=False, long=False, print_tail=False):
    if not isa_rundir(runid):
        # we're not inspecting a run; try environment
        return inspect_experiment(runid, variable_name=variable_name, long=long)

    try:
        runid = runid.split('-debug')[0]
        allruns = list_all_rundirs()
        mypath = [run for run in allruns if runid in run][0]

    except ValueError:
        print('couldn\'t find that run')
        return

    # print('looking in {}'.format(mypath))

    runlog = os.path.join(mypath, DIRNAMES.ROOT_LOG)
    metadata = os.path.join(mypath, 'xanity_metadata.dill')
    parameters = os.path.join(mypath, DIRNAMES.RUN_PARAMETERS)
    exps = {}

    for d in os.listdir(mypath):
        sdir = os.path.join(mypath, d)
        if os.path.isdir(sdir):
            exps.update({d: {'path': sdir, 'subexps': []}})

    for exp, ed in exps.items():
        exp_cont = os.listdir(ed['path'])
        for item in exp_cont:
            ipath = os.path.join(ed['path'], item)
            if fnmatch(item, exp + '_*') and os.path.isdir(ipath):
                ed['subexps'].append(ipath)

    print('')

    if print_head:
        if os.path.isfile(runlog):
            # print('head of runlog')
            h_rule = 0
            with open(runlog, 'r') as f:
                f.readline()
                for line in f:
                    if '##################################' in line:
                        if h_rule < 1:
                            h_rule += 1
                        else:
                            break
                    else:
                        print(line.rstrip())
        print('\n')
        return

    if print_tail:
        subprocess.call(['tail', '-n', '10', runlog])
        print('')
        return

    logfiles = [os.path.join(rroot, file) for exp, ed in exps.items() for rroot, _, files in os.walk(ed['path']) for
                file in files if fnmatch(file, '*xanity*.log')]

    varpaths = [os.path.join(rroot, ddir) for exp, ed in exps.items() for rroot, sdir, _ in os.walk(ed['path']) for ddir
                in sdir if
                fnmatch(ddir, 'xanity_variables')]

    subexp_ct = sum([len(exp['subexps']) for exp in exps.values()])

    print(' {:>25}    {:<}'.format(
        'experiments:',
        len(exps) if not subexp_ct else subexp_ct
    ))

    # print(' {:>25}    {:<}'.format(
    #     'subexperiments:',
    #     sum([ len(exp['subexps']) for exp in exps.values() ])))

    if len(logfiles) > 0:
        print(' {:>25}    {:<}'.format(
            'experiment logs:', '{}, {:^}'.format(
                len(logfiles),
                sizeof_fmt(sum([get_n_bytes(item) for item in logfiles])),
            ))
        )

    print(' {:>25}    {:<}'.format(
        'saved xanity variables:', '{}, {:^}'.format(
            sum([len(os.listdir(pp)) for pp in varpaths]),
            sizeof_fmt(sum([get_n_bytes(item) for item in varpaths])),
        ))
    )

    print(' {:>25}    {:<}'.format(
        '=========================', '=============')
    )

    print(' {:>25}    {:<}'.format(
        'total size:', '{}, {:^}'.format(
            len(subprocess.check_output(['find', mypath, '-type', 'f']).decode().split()),
            sizeof_fmt(get_n_bytes(mypath))
        ))
    )

    if long:
        if os.path.isfile(parameters):
            try:
                info = pickle_load(parameters)
                print('')
                for name, val in info.items():
                    print(' {:>25}    {:<}'.format(
                        name + ':', str(val).decode())
                    )
            except:
                pass

        names = list(set([file.split('.dill')[0] for path in varpaths for file in os.listdir(path)]))
        print('')
        print(' {:>25}    {:<}'.format(
            'variable names:', names)
        )

    print('\n')


def resolve_upanddown(path, target):
    if not path.split(os.sep)[-1] == target:
        if target not in os.listdir(path):
            path = os.path.split(path)[0]
        else:
            path = os.path.join(path, target)
        if target not in os.listdir(path):
            print('get_parameter dict can only look up/down one dir level')
            return None
        else:
            path = os.path.join(path, target)

    return path


def get_parameter_dict(xanity_data_path):
    subdirpath = resolve_upanddown(xanity_data_path, 'xanity_variables')
    pdicts = []
    param_prelude = (EXPERIMENT_LOG_HEADER.split('starting experiment')[0] + 'starting experiment').split('\n')[-1]

    pathparts = subdirpath.split(os.sep)
    root_part = [i for i, item in enumerate(pathparts) if isa_rundir(item)]
    assert sum([item > 0 for item in root_part]) == 1
    root_ind = sum(root_part)
    rundir = os.sep.join(pathparts[:root_ind + 1])
    run_id, expname, subexpind = split_rundir(rundir)
    vardir = os.path.join(rundir, DIRNAMES.SAVED_VARS)

    def parse_headblock(file):

        pdicts = []

        with open(file, 'r') as f:
            text = ''
            foundit = False
            for line in f.readlines():
                if not foundit:
                    if re.match(param_prelude, line):
                        foundit = True
                else:
                    if '############' not in line:
                        text += line
                    else:
                        break

        rows = [item.split(',') for item in re.findall('.*{(.*)}.*', text)]

        for row in rows:
            pdict = {}
            for i, entry in enumerate(row):
                opens = sum([item == '(' for item in entry])
                closes = sum([item == ')' for item in entry])
                if closes > opens:
                    break
                while opens > closes:
                    entry += ',' + row[i + 1]
                    closes = sum([item == ')' for item in entry])

                key, val = entry.split(':')
                key = key.strip(' "\'')
                if ',' in val:
                    ilist = []
                    for item in val.split(','):
                        item = item.strip(' [()]')
                        if item:
                            ilist.append(float(item))
                        val = tuple(ilist)
                else:
                    val = float(val.strip(' [()]'))
                pdict.update({key: val})

            pdicts.append(pdict)

        return pdicts

    if os.path.isfile(os.path.join(vardir, DIRNAMES.RUN_PARAMETERS)):
        pdicts = [try_load(os.path.join(vardir, DIRNAMES.RUN_PARAMETERS))]

    if not pdicts and os.path.isfile(os.path.join(rundir, DIRNAMES.RUN_PARAMETERS)):
        pdicts = [try_load(os.path.join(rundir, DIRNAMES.RUN_PARAMETERS))]

    # if not pdicts and metarundir and os.path.isfile(os.path.join(metarundir, DIRNAMES.RUN_PARAMETERS)):
    #     pdicts = [try_load(os.path.join(metarundir, DIRNAMES.RUN_PARAMETERS))]

    # try log files:
    if not pdicts:

        # look for per-subexperiment logfile
        files = os.listdir(rundir)

        for ff in files:
            if fnmatch(ff, '*xanity*.log'):
                pdicts = parse_headblock(os.path.join(rundir, ff))

    # if not pdicts and metarundir:
    #
    #     # look for per-experiment logfile
    #     files = os.listdir(metarundir)
    #
    #     for ff in files:
    #         if fnmatch(ff, '*xanity*.log'):
    #             pdicts = parse_headblock(os.path.join(metarundir, ff))

    if not pdicts:

        # look for per-experiment logfile
        files = os.listdir(rundir)

        for ff in files:
            if fnmatch(ff, '*' + DIRNAMES.LOG_SUFFIX):
                pdicts = parse_headblock(os.path.join(rundir, ff))

    if not pdicts:
        pdicts = [{}]

    if len(pdicts) > 1:
        if not subexp:
            raise ValueError('got parameter array in a non-subexperiment setting')
        raise NotImplementedError
    else:
        return pdicts[0]


def fetch_timer_data(experiment=None, reduce=None):
    data = fetch_variable(experiment=experiment, variable='xanity_timed_fn_dict')
    outdata = pd.DataFrame()

    for index, tdict in data.xanity_timed_fn_dict.iteritems():
        newframe = pd.DataFrame()
        for item, value in tdict.items():
            names = [item + '_timer_' + str(i) for i in range(len(value))]
            if callable(reduce):
                value = reduce(value)
            newframe = pd.concat([newframe, pd.DataFrame(dict(zip(names, value)), index=[index])], axis=1, )
        outdata = pd.concat([outdata, newframe], axis=0, sort=False)

    return pd.concat(
        [
            data.drop('xanity_timed_fn_dict', axis=1),
            outdata,
        ],
        axis=1,
        sort=False
    )


def list_xanity_variables(experiment=None, path=None, runid=None):
    if not experiment and not path and not runid:
        raise ValueError('must give either an experiment or a path')

    variables = set()

    if experiment is not None:
        if isinstance(experiment, str):
            experiment = [experiment]
        for exp in experiment:
            for bd, sds, fs in os.walk(exp):
                if os.path.split(bd)[-1] == 'xanity_variables':
                    variables.update(set(tuple(item.split('.dill')[0] for item in fs if fnmatch(item, '*.dill'))))

    elif path is not None:
        for bd, sds, fs in os.walk(path):
            if os.path.split(bd)[-1] == 'xanity_variables':
                variables.update(set(tuple(item.split('.dill')[0] for item in fs if fnmatch(item, '*.dill'))))

    elif runid is not None:
        path = runid2path(runid)
        for bd, sds, fs in os.walk(path):
            if os.path.split(bd)[-1] == 'xanity_variables':
                variables.update(set(tuple(item.split('.dill')[0] for item in fs if fnmatch(item, '*.dill'))))

    return list(variables)


def find_xanity_variable(name):
    all_runs = list_all_rundirs()
    locations = []
    for run in all_runs:
        for bd, sds, fs in os.walk(run):
            if os.path.split(bd)[-1] == 'xanity_variables' and name + '.dill' in fs:
                locations.append(bd)
    return locations


def fetch_variable(variable, experiment=None, runids=None, most_recent=True, verbose=False):
    all_runs = get_rundirs(experiments=experiment)

    if isinstance(runids, str):
        runids = [runids]

    if runids:
        all_runs = [run for run in all_runs if any([rrun in run for rrun in runids])]

    if not all_runs:
        return None

    results = []

    for run in all_runs:
        for bd, sds, fs in os.walk(run):

            if os.path.split(bd)[-1] == 'xanity_variables' and variable + '.dill' in fs:

                pdicts = get_parameter_dict(bd)

                try:
                    run_id, expname, subexpind = split_rundir(os.path.split(bd)[-2])
                except:
                    continue

                value = try_load(os.path.join(bd, variable + '.dill'))
                if value is None:
                    continue

                record = {
                    'exp_name': expname,
                    'exp_index': subexpind,
                    'run_id': run_id,
                    'UID': '_'.join([run_id, expname, subexpind]),
                    variable: value,
                }

                if pdicts:
                    if isinstance(pdicts, list) and len(pdicts) > 1:
                        raise NotImplementedError
                    else:
                        record.update(pdicts)

                results.append(record)
                print('loaded {}'.format(record['UID'])) if verbose else None

    if most_recent:
        results = results[-1] if len(results) > 0 else None

    return pd.DataFrame([results]).set_index('UID', drop=True) if results else None


def load_data(experiments=None, variables=None, reduce=None, most_recent=False, runids=None):
    """
    loops through multiple experiment names and variable names,

    :param experiments:
    :param variables:
    :param reduce: dict of {fn:[columns],...} or list of tuples: [(column, fn),...]
    :return: a pandas Dataframe object
    """

    if isinstance(experiments, str):
        experiments = [experiments]
    if isinstance(variables, str):
        variables = [variables]
    if isinstance(runids, str):
        runids = [runids]

    if not experiments and not variables:
        try:
            if not confirm(
                    'you\'re about to load all data from all experiments... this could be bad news for your system memory.',
                    default_response=False):
                return

        except KeyboardInterrupt:
            print('')
            return

    if experiments is None and not runids:
        experiments = list_all_experiments()

    if reduce is not None:
        if callable(reduce):
            # a single fn was given, apply everywhere:
            reduce = {reduce: [v for v in variables]}

        elif isinstance(reduce, dict):
            for k, v in reduce.items():
                if not isinstance(v, list):
                    reduce[k] = [v]

        elif isinstance(reduce, (list, tuple)):
            rd = {}
            if isinstance(reduce[0], (list, tuple)):
                for item in reduce:
                    assert len(item) == 2
                    if not callable(item[0]):
                        assert callable(item[1])
                        rd.update({item[1]: item[0]})
                    else:
                        assert callable(item[0])
                        rd.update({item[0]: item[1]})

            else:
                if not callable(reduce[0]):
                    assert callable(reduce[1])
                    rd.update({reduce[1]: reduce[0]})
                else:
                    assert callable(reduce[0])
                    rd.update({reduce[0]: reduce[1]})

            reduce = rd

        elif callable(reduce):
            reduce = {reduce, '*'}

        elif isinstance(reduce, str):
            if hasattr(pd.DataFrame, reduce):
                reduce = {getattr(pd.DataFrame, reduce), '*'}

        reduction_targs = set()
        for item in reduce.values():
            if isinstance(item, str):
                reduction_targs.update(set(item))
            else:
                reduction_targs.update(set(item))
        reduction_targs = list(reduction_targs)

    df = pd.DataFrame()
    for var in variables:
        # these will be concatenated on axis 1

        df1 = pd.DataFrame()
        if runids:
            for rid in runids:
                data = fetch_variable(variable=var, most_recent=most_recent, runids=rid)
                if data is None:
                    continue
                if reduce is not None:
                    for rtarg in reduction_targs:
                        if any([re.match(rtarg, item) for item in data.columns.values]):
                            fn = [fn for fn, targs in reduce.items() if rtarg in targs][0]
                            data = reduce_column(data, fn, rtarg)
                df1 = pd.concat([df1, data], axis=0, sort=False)
        else:
            for exp in experiments:
                # these will be concatenated on axis 0

                data = fetch_variable(experiment=exp, variable=var, most_recent=most_recent)
                if data is None:
                    continue
                if reduce is not None:
                    for rtarg in reduction_targs:
                        if any([re.match(rtarg, item) for item in data.columns.values]):
                            fn = [fn for fn, targs in reduce.items() if rtarg in targs][0]
                            data = reduce_column(data, fn, rtarg)
                df1 = pd.concat([df1, data], axis=0, sort=False)
        df = pd.concat([df, df1], axis=1, sort=False)

    return df


def reduce_column(df, fn, column_name):
    # reduce eval record data
    inds = []
    vals = []
    cts = []

    col = df.filter(regex=column_name, axis=1)
    column_name = col.columns.values[0]

    for index, data in col.iterrows():
        inds.append(index)
        vals.append(fn(data.values[0].flatten()))
        cts.append(len(data))

    return pd.concat([
        df.drop(column_name, axis=1),
        pd.DataFrame(data={'num_' + column_name: cts, 'reduced_' + column_name: vals}, index=inds),
    ], axis=1, sort=False)


# ###############################################
# Main, module-level, parser:


class DataParser(argparse.ArgumentParser):
    def __init__(self):
        super(DataParser, self).__init__(prog='xanity-data', add_help=False, usage=generate_help_text())
        self.add_argument('action')

    def parse_and_call(self, *args, **kwargs):

        kn, unk = self.parse_known_args(*args, **kwargs)
        from . import xanity as _xanity
        _xanity._orient()
        get_root()

        if not XANITY_ROOT:
            print('run \'xanity data\' from inside xanity project tree or use \'xanity data --data-path /path/to/my/data ...\'')
            raise SystemExit

        if kn.action in DATA_COMMANDS:
            DATA_COMMANDS[kn.action].entry(unk)

        else:
            print('unknown xanity-data command. Use \'xanity data --help\' for help.')
            raise SystemExit


# Subordinate Parsers:

class ScoreParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ScoreParser, self).__init__(*args, prog='xanity-data', **kwargs)
        self.add_argument('--composite', '-C', action='store_true', help='sort by a composite of score and size')
        self.add_argument('--size', '-s', action='store_true', help='sort by size')
        self.add_argument('--score', '-S', help='sort by score')
        self.add_argument('--headings', '-H', action='store', type=int, default=20)
        self.add_argument('--normalize', '-n', action='store_true')
        # self.add_argument('--logarithmic','-L', action='store_true', default=True)
        self.add_argument('--ascending', '-a', action='store_true')
        self.add_argument('--descending', '-d', action='store_true')
        self.add_argument('--top', '-t', default=0)
        self.add_argument('--name', '-N', action='store_true')
        self.add_argument('--alpha', action='store_true')
        self.add_argument('selectors', nargs='*', type=str)


class SummarizeParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(SummarizeParser, self).__init__(*args, prog='xanity-data', **kwargs)
        self.add_argument('--top', '-t', type=int, default=4)
        self.add_argument('--columns', '-c', type=int, default=2)
        self.add_argument('selectors', nargs='*', type=str)


class PruneParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(PruneParser, self).__init__(*args, prog='xanity-data', **kwargs)
        self.add_argument('selectors', nargs='*', default=['all'])
        self.add_argument('--threshold', '-t', type=str, default='0.001')
        self.add_argument('--metric', '-m', type=str, default='size')
        self.add_argument('--unit', '-u', type=str)
        self.add_argument('--human-readable', '-H', action='store_true')
        self.add_argument('--path', '-p', action='store_true')
        self.add_argument('--full-path-only', '-P', action='store_true')
        self.add_argument('--delete', '-D', action='store_true')
        self.add_argument('--count-only', '-c', action='store_true')
        self.add_argument('--saved', action='store_true')
        self.add_argument('--scores', '-s', action='store_true')


class InspectParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(InspectParser, self).__init__(*args, prog='xanity-data', **kwargs)
        self.add_argument('run_id')
        self.add_argument('variable_name', nargs='?', default=None)
        self.add_argument('--long', '-l', action='store_true', help='prints variable names')
        self.add_argument('--log', '-L', action='store_true', help='prints head of root log')
        self.add_argument('--end', '-e', action='store_true', help='prints tail of root log')
        self.add_argument('--variable', '-v', action='store_true', help='indicates that the arg is a variable')
        self.add_argument('--experiment', '-E', action='store_true', help='indicates that the arg is a variable')


class PurgeParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(PurgeParser, self).__init__(*args, prog='xanity-data', **kwargs)
        self.add_argument('selectors', nargs='*', type=str)


class ListParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ListParser, self).__init__(*args, prog='xanity-data', **kwargs)
        self.add_argument('--count-only', '-c', action='store_true', help='print only the count')
        self.add_argument('selectors', nargs='*', help='complete, incomplete, failed, successful')


# ##################################
# Subordinate entry-points :

def score_entry(args=None):
    kn = ScoreParser().parse_args(args)

    if kn.composite:
        sort = 'composite_score'
    elif kn.size:
        sort = 'size'
    elif kn.score:
        sort = 'score'
    elif kn.alpha or kn.name:
        sort = 'alpha'
    else:
        sort = 'size'

    if kn.ascending and not kn.descending:
        order = 'ascending'
    elif kn.descending and not kn.ascending:
        order = 'ascending'
    elif not kn.descending and not kn.ascending:
        order = 'descending'
    else:
        raise ValueError('conflicting order requests,')

    dirs = select_rundirs(**parse_selectors(kn.selectors))
    if dirs:
        scan_data(rundirs=dirs, print_results=True, sort=sort, order=order, top=kn.top, headings=kn.headings,
                  normalize=kn.normalize)


def summarize_entry(args=None):
    kn = SummarizeParser().parse_args(args)
    dirs = select_rundirs(**parse_selectors(kn.selectors))
    if dirs:
        summarize_data(rundirs=dirs, top=kn.top, cols=kn.columns, exp_summary=not kn.selectors)


def prune_entry(args=None):
    kn = PruneParser().parse_args(args)
    dirs = select_rundirs(**parse_selectors(kn.selectors))
    if dirs:
        prune(rundirs=dirs, threshold=kn.threshold, metric=kn.metric, unit=kn.unit,
              human_readable=kn.human_readable, full_path=kn.path,
              full_path_only=kn.full_path_only, delete=kn.delete, count_only=kn.count_only,
              include_saved=kn.saved, print_scores=kn.scores)


def inspect_entry(args=None):
    kn = InspectParser().parse_args(args)
    if kn.variable:
        inspect_variable(kn.run_id, long=kn.long)
    elif kn.experiment:
        inspect_experiment(kn.run_id, long=kn.long)
    elif isa_rundir(kn.run_id):
        inspect_run(kn.run_id, kn.variable_name, long=kn.long, print_head=kn.log, print_tail=kn.end)
    else:
        print('didn\'t recognize that request')


def purge_entry(args=None):
    kn = PurgeParser().parse_args(args)
    purge(**parse_selectors(kn.selectors))


def list_entry(args=None):
    kn = ListParser().parse_args(args)
    if not kn.selectors:
        kn.selectors = ['all']
    selection = parse_selectors(kn.selectors)
    dirs = select_rundirs(**selection)
    if dirs:
        if kn.count_only:
            print(len(dirs))
        else:
            print('\n'.join(dirs))


# Associate commands with their aliases and entry-points:
DATA_COMMANDS = CommandSet({
    'prune': (['prune'], prune_entry),
    'score': (['score', 'scores', 'scan'], score_entry),
    'summarize': (['summary', 'summarize'], summarize_entry),
    'inspect': (['inspect'], inspect_entry),
    'purge': (['purge'], purge_entry),
    'list': (['list'], list_entry),
})


def generate_help_text():
    text = " xanity data action [--help|-h]\n\n   xanity-data invoked without specifying an action. Available actions include: \n\n{}".format(
        '\n'.join(['   {} [--help]'.format('|'.join(item.aliases)) for item in DATA_COMMANDS])
    )
    return text


def main(*args):
    DataParser().parse_and_call(*args) if args else DataParser().parse_and_call()


if __name__ == '__main__':
    main()


def __main__(*args, **kwargs):
    main(*args, **kwargs)
