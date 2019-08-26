#----------------------------------------------------------------------
# Copyright 2018 Marco Inacio <pythonpackages@marcoinacio.com>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, version 3 of the License.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------

import numpy as np
import itertools
from collections import OrderedDict
import peewee
import pickle

def process_binary(dict_, Result):
    for k in dict_:
        if type(getattr(Result, k)) == peewee.BlobField:
            if type(dict_[k]) != bytes:
               dict_[k] = pickle.dumps(dict_[k])

def do_simulation_study(to_sample, func, db, Result, max_count=1,
    sample_filter=None):
    to_sample = OrderedDict(to_sample) # ensure order won't be messed up
    full_sample = set(itertools.product(*to_sample.values()))
    keys = list(to_sample)

    while full_sample:
        sample = np.random.choice(len(full_sample))
        sample = list(full_sample)[sample]
        dsample = dict(zip(keys, sample))
        if sample_filter is not None and not sample_filter(**dsample):
            #print("Discarded combination")
            full_sample.discard(sample)
            continue

        # check count of rows in db
        clean_dsample = dsample.copy()
        process_binary(dsample, Result)
        query = Result.select().where(
            *[getattr(Result, x[0]) == x[1] for x in dsample.items()]
            )
        print(len(full_sample), "combinations left")
        if query.count() >= max_count:
            full_sample.discard(sample)
            continue
        db.close()

        func_res = func(**clean_dsample)
        process_binary(func_res, Result)

        print("Results:")
        print({
            k:(v if type(v) != bytes else "binary blob")
            for k, v in func_res.items()
        })

        Result.create(**dsample, **func_res)
        print("Result stored in the database", flush=True)
