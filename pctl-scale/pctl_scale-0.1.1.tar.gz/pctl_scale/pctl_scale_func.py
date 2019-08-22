import numpy as np


def saturate_upper_to_one(x, b):
    t = x - b
    k = 1 / (1 - b)
    return b / (b + (1 - b) * np.exp(-t * k))


def saturate_lower_to_zero(x, a):
    t = a - x
    k = 1 / a
    return a / np.exp(t * k)


def percentile_scale_clean(x, a=.05, b=.95):
    # compute upper and lower pctl values
    va, vb = np.percentile(x, q=(a * 100, b * 100))

    # scale x=[va,vu] to y=[a,b]
    to1 = (x - va) / (vb - va)
    y = a + b * to1

    # saturate upper values to [b,1]
    idx = y > b
    y[idx] = saturate_upper_to_one(y[idx], b)

    # fit lower values to [0,a]
    idx = y < a
    y[idx] = saturate_lower_to_zero(y[idx], a)

    # done
    return y, va, vb


def check_ignore(e, naignore=[]):
    """True if the element is nan, inf, None, or
    from a specified list with excluded values
    """
    if e:   # Check None
        if np.isnan(e):
            return True
        if np.isinf(e):
            return True
        if naignore:
            if e in naignore:
                return True
    else:
        return True
    return False


def percentile_scale(x, a=.05, b=.95, naignore=[0], naimpute=0):
    # ensure numpy array
    x_ = np.array(x)
    # memorize ineligible values
    idxmiss = np.array([check_ignore(e, naignore) for e in x_])
    idxexist = np.logical_not(idxmiss)

    y, va, vb = percentile_scale_clean(x_[idxexist], a=a, b=b)

    z = np.empty(shape=x_.shape)
    z[idxexist] = y
    z[idxmiss] = naimpute

    return z, va, vb


def inverse_ztoy_upper(z, b):
    oneminusb = 1 - b
    return b - oneminusb * np.log(((b / z) - b) / oneminusb)


def inverse_ztoy_lower(z, a):
    return a * (np.log(z / a) + 1)


def inverse(z, a, b, va, vb):
    # the linear case z=y (nothing to inverse. just copy)
    y = z.copy()

    # inverse z below threshold a
    idx = z < a
    y[idx] = inverse_ztoy_lower(z[idx], a)

    # inverse z above threshold b
    idx = z > b
    y[idx] = inverse_ztoy_upper(z[idx], b)

    # inverse the min-max scaling y to x
    return ((y - a) / b) * (vb - va) + va
