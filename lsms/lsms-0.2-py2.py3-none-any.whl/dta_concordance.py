
# -*- coding: utf-8 -*-

import sys
try: # Only if python 2
    reload(sys).setdefaultencoding('utf-8')
except NameError: pass 
import pandas as pd
from pandas.io import stata
from glob import glob
from collections import defaultdict
from warnings import warn

def dta_concordance(dir):
    dtafiles=glob(dir+'*.dta')

    lbls={}
    concordance=defaultdict(list)
    for fn in dtafiles:
        try:
            sr=stata.StataReader(fn)
        except ValueError as failed:
            warn("Can't read %s; %s" % (fn,failed.message))
            continue
        new=sr.variable_labels()
        lbls.update(new)
        for k in new.keys():
            concordance[k].append(fn)

    for k in sorted(list(concordance.keys())):
        print("| %s | %s | " % (k,lbls[k]), end='')
        for f in concordance[k]:
            print(f,end=' ')
        print("|")
