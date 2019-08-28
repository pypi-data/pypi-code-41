
def deriv_check_ratio(func, x, eps):
    import numpy as np
    s1 = func(x)
    step = eps * np.random.rand(len(x))
    s2 = func(np.asarray(x).flatten() + step.flatten())
    rdiff = (s2.r - s1.r).flatten()
    rdiff_pred = s1.dr_wrt(x).dot((np.zeros_like(x).flatten() + step.flatten()))
    return rdiff / rdiff_pred


class ExtraAssertionsMixin(object):
    def assertAlmostEqual(self, a, b, places=7, msg='', delta=None, sigfigs=None):
        if sigfigs is None:
            super(ExtraAssertionsMixin, self).assertAlmostEqual(a, b, places, msg, delta)
        else:
            a_ = float(('%%.%dg' % sigfigs) % a)
            b_ = float(('%%.%dg' % sigfigs) % b)
            if a_ != b_:
                raise AssertionError(msg or "%f != %f to %d significant figures (%f != %f)" % (a, b, sigfigs, a_, b_))

    def assertDictOfArraysEqual(self, a, b, msg=''):
        import numpy as np
        self.assertIsInstance(a, dict, msg or 'First argument is not a dictionary')
        self.assertIsInstance(b, dict, msg or 'Second argument is not a dictionary')
        self.assertSetEqual(set(a.keys()), set(b.keys()), msg or 'Keys do not match')
        for k in a.keys():
            if isinstance(a[k], np.ndarray) and isinstance(b[k], np.ndarray):
                np.testing.assert_array_equal(a[k], b[k], err_msg=msg + "\nwith key [%s]" % (k))
            else:
                np.testing.assert_array_equal(np.array(a[k]), np.array(b[k]), err_msg=msg + "\nwith key [%s]" % (k))

    def assertDictOfArraysAlmostEqual(self, a, b, decimal=6, msg=''):
        import numpy as np
        self.assertIsInstance(a, dict, msg or 'First argument is not a dictionary')
        self.assertIsInstance(b, dict, msg or 'Second argument is not a dictionary')
        self.assertSetEqual(set(a.keys()), set(b.keys()), msg or 'Keys do not match')
        for k in a.keys():
            if isinstance(a[k], np.ndarray) and isinstance(b[k], np.ndarray):
                np.testing.assert_array_almost_equal(a[k], b[k], decimal=decimal, err_msg=msg + "\nwith key [%s]" % (k))
            else:
                np.testing.assert_array_almost_equal(np.array(a[k]), np.array(b[k]), decimal=decimal, err_msg=msg + "\nwith key [%s]" % (k))

    def assertTextEqual(self, candidate_text, truth_text, candidate_path='', truth_path=''):
        import difflib
        diff = difflib.unified_diff(truth_text.splitlines(True), candidate_text.splitlines(True), fromfile=truth_path+" (expected)", tofile=candidate_path+" (actual)")
        self.assertEqual(candidate_text, truth_text, msg="Files differ\n" + "".join(diff))

    def assertFilesEqual(self, candidate_path, truth_path):
        from baiji import s3
        with s3.open(candidate_path, 'rb') as f:
            candidate = f.read()
        with s3.open(truth_path, 'rb') as f:
            truth = f.read()
        self.assertTextEqual(candidate, truth, candidate_path, truth_path)

    def assertDerivativeEquals(self, func, x, expected_dx, eps, decimal=6, err_msg=''):
        import numpy as np
        dcr = deriv_check_ratio(func, x, eps)
        np.testing.assert_array_almost_equal(dcr, expected_dx, decimal=decimal, err_msg=err_msg)

    def assertSparseArrayEqual(self, a, b):
        self.assertEqual((a != b).nnz, 0)
