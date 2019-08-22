import unittest
from pctl_scale import percentile_scale, inverse, PercentileScaler
import numpy.testing as npt
import numpy as np


class Test_inverse_transform(unittest.TestCase):

    def test1(self):
        lower = .05
        upper = .95
        x = np.random.normal(0, 1, (1000,))
        z, va, vb = percentile_scale(x, a=lower, b=upper)
        xinv = inverse(z, lower, upper, va, vb)
        npt.assert_array_almost_equal(xinv, x, decimal=7)

    def test2(self):
        lower = .05
        upper = .95
        x = np.random.normal(0, 1, (1000,))
        scl = PercentileScaler(upper=upper, lower=lower)
        z = scl.fit_transform(x)
        xinv = scl.inverse_transform(z)
        npt.assert_array_almost_equal(xinv, x, decimal=7)


# run
if __name__ == '__main__':
    unittest.main()
