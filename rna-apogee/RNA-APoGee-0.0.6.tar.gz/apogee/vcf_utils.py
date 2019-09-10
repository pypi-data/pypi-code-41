import re
import numpy as np


def rec_is_passing(rec):
    return rec.FILTER == 'PASS' or rec.FILTER == []


def gt_to_int(gt):
    return 0 if gt == '.' else int(gt)


def get_rec_gt(geno):
    gt = geno['GT']
    gt_split = re.compile('\||/')
    return np.sum([gt_to_int(s) for s in gt_split.split(gt)])


def get_rec_field(geno, field, default=0):
    try:
        out = getattr(geno.data, field, default)
    except Exception:
        out = default
    if out is None:
        out = default
    return out
