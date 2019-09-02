from .Assert import *
# -----------------------------------------------


# -----------------------------------------------
def fact(n):
    Assert(n >= 0, 'fact error: ' + str(n), cf())

    if n == 0:
        return 1

    f = 1

    while n > 0:
        f *= n
        n -= 1

    return f
# -----------------------------------------------


# -----------------------------------------------
def C_n_k(n, k):
    Assert(n >= 0, 'C_n_k error', cf())
    Assert(k >= 0, 'C_n_k error', cf())

    return fact(n) / fact(k) / fact(n - k)
# -----------------------------------------------


# -----------------------------------------------
class Cnk:

    def __init__(self, max_n):
        self.cnk = dict()

        for n in range(max_n + 1):
            for k in range(n + 1):
                self.cnk[str(n) + '_' + str(k)] = C_n_k(n, k)
        return

    def get(self, n, k):
        v_found = None

        for _k, _v in self.cnk.items():
            if _k == (str(n) + '_' + str(k)):
                v_found = _v
                break

        Assert(v_found is not None, "Cnk not found: n = " +
               str(n) + ', k = '+str(k), cf())

        return v_found


# -----------------------------------------------
