# Copyright (c) 2018-2019, Eduardo Rodrigues and Henry Schreiner.
#
# Distributed under the 3-clause BSD license, see accompanying file LICENSE
# or https://github.com/scikit-hep/particle for details.

from __future__ import absolute_import

import csv

from .. import data
from ..pdgid import PDGID


with data.open_text(data, 'pdgname_to_evtgenname.csv') as _f:
    _bimap = {v['EVTGENNAME']:v['NAME'] for v in csv.DictReader(_f)}


class EvtGenName(str):
    pass
