"""
@file
@brief Metrics about regressions.
"""
import io
import numpy
import pandas


def l1_reg_max(exp, val, max_val=180, nomax=False, exc=True):
    """
    Implements a :epkg:`L1` scoring function which does not consider
    error above threshold *max_val*.

    @param      exp         list of values or :epkg:`numpy:array`
    @param      val         list of values or :epkg:`numpy:array`
    @param      max_val     every value above *max_val* is replaced by *max_val*
                            before computing the differences
    @param      nomax       removes every value equal or above *nomax* in expected set,
                            then compute the score
    @param                  raises an exception if not enough submitted items
    @return                 score

    If ``max_val==180``, the function computes:

    .. math::

        E = \\frac{1}{n} \\sum_{i=1}^n \\frac{\\left| \\min (Y_i, 180) - \\min(f(X_i), 180) \\right|}{180}

    The computation is faster if :epkg:`numpy:array` are used
    (for *exp* and *val*). *exp and *val* can be filenames or streams.
    In that case, the function expects to find two columns: id, value
    in both files or streams.
    """
    if isinstance(exp, numpy.ndarray) and isinstance(val, numpy.ndarray):
        if len(exp) != len(val):
            raise ValueError(
                "Dimension mismatch {0} != {1}".format(len(exp), len(val)))
        an = numpy.zeros((len(exp),))
        an[:] = max_val
        mv = numpy.minimum(an, val)  # pylint: disable=E1111
        me = numpy.minimum(an, exp)  # pylint: disable=E1111
        if nomax:
            mv = mv[me < max_val]
            me = me[me < max_val]
        df = numpy.abs(mv - me) / max_val
        return df.mean()
    elif isinstance(exp, dict) and isinstance(val, dict):
        if exc and len(exp) != len(val):
            number_common = len(set(exp) & set(val))
            raise ValueError(
                "Dimension mismatch {0} != {1} (#common={2})".format(len(exp), len(val), number_common))
        r = 0.0
        nb = 0
        for k, e in exp.items():
            if k in val:
                v = val[k]
                try:
                    mv = min(v, max_val)
                except TypeError:
                    return numpy.nan
                try:
                    ev = min(e, max_val)
                except TypeError:
                    return numpy.nan
                if nomax and ev >= max_val:
                    continue
                d = abs(mv - ev)
                r += 1. * d / max_val
                nb += 1
            elif exc:
                raise ValueError("Missing key in prediction {0}".format(k))
            else:
                r += 1.
                nb += 1
        return r / nb if nb > 0 else 0.0
    elif isinstance(exp, (str, io.StringIO)) and isinstance(val, (str, io.StringIO)):
        # We expect filenames.
        d1 = pandas.read_csv(exp, header=None, sep=";")
        d2 = pandas.read_csv(val, header=None, sep=";")
        dd1 = {}
        for k, v in d1.itertuples(name=None, index=False):
            if k in dd1:
                raise KeyError("Key '{}' present at least twice.".format(k))
            dd1[k] = v
        dd2 = {}
        for k, v in d2.itertuples(name=None, index=False):
            if k in dd2:
                raise KeyError("Key '{}' present at least twice.".format(k))
            dd2[k] = v
        return l1_reg_max(dd1, dd2, max_val=max_val, nomax=nomax, exc=exc)
    elif isinstance(exp, list) and isinstance(val, list):
        if len(exp) != len(val):
            raise ValueError(
                "Dimension mismatch {0} != {1}".format(len(exp), len(val)))
        r = 0.0
        nb = 0
        for e, v in zip(exp, val):
            ev = min(e, max_val)
            if nomax and ev >= max_val:
                continue
            mv = min(v, max_val)
            d = abs(mv - ev)
            r += 1. * d / max_val
            nb += 1
        return r / nb if nb > 0 else 0.0
    else:
        raise TypeError(
            "Inconsistent types {0} != {1}".format(type(exp), type(val)))
