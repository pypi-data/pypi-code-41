import unittest
from ComStats import comstats
import numpy as np

class TestComStats(unittest.TestCase):

    def setUp(self):
        self.input_set = np.array([
            [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1],
            [2, 1, 2, 3, 3, 0, 1, 0, 0, 0, 4, 1, 2, 4, 4],
            [1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0],
            [3, 0, 1, 3, 0, 0, 2, 1, 2, 3, 3, 1, 0, 0, 2]
        ])
        self.weights = np.array([
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1],
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1],
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1],
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1]
        ])
        self.percentage_input_set = np.array([
            [0.1, 0.05, 0.05, 0.1, 0.6, 0.0, 0.4, 0.1, 0.1, 0.05, 0.1, 0.0, 0.0, 0.0, 0.1],
            [0.3, 0.05, 0.1, 0.3, 0.5, 0.2, 0.21, 0.1, 0.2, 0.3, 0.3, 0.1, 0.0, 0.0, 0.2]
        ])
        self.percentage_weights = np.array([
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1],
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1]
        ])
        self.percentage_weights = np.array([
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1],
            [1, 0.1, 0.2, 0.3, 2, 0.1, 0.1, 2, 0.1, 0.1, 0.2, 0.1, 0.3, 0.4, 1]
        ])
        self.sample_sizes_set = np.array([
            [20, 50, 10, 12, 25]
        ])
        self.count_set = np.array([
            [11, 20, 8, 3, 18]
        ])
        self.population_proportion_set = np.array([
            [0.5, 0.3, 0.7, 0.4, 0.6]
        ])
        self.binary_sample_input_set = np.array([
            [1, 0, 1, 1, 1, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 0, 1]
        ])
        self.population_proportion_scalar = 0.7


    def test_unweighted_t_test(self):
        expected_p_values = [[ 1.        ,  0.00353093,  1.        ,  0.00961514],
                             [ 0.00353093,  1.        ,  0.00353093,  0.43711409],
                             [ 1.        ,  0.00353093,  1.        ,  0.00961514],
                             [ 0.00961514,  0.43711409,  0.00961514,  1.        ]]
        expected_scores = [[ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 3.38132124,  0.        ,  3.38132124,  0.78881064],
                           [ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 2.88675135, -0.78881064,  2.88675135,  0.        ]]
        p_values, scores = comstats.t_test(self.input_set)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_unweighted_t_test_one_sided(self):
        expected_p_values = [[ 0.5       ,  0.00176546,  0.5       ,  0.00480757],
                             [ 0.00176546,  0.5       ,  0.00176546,  0.21855705],
                             [ 0.5       ,  0.00176546,  0.5       ,  0.00480757],
                             [ 0.00480757,  0.21855705,  0.00480757,  0.5       ]]
        expected_scores = [[ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 3.38132124,  0.        ,  3.38132124,  0.78881064],
                           [ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 2.88675135, -0.78881064,  2.88675135,  0.        ]]
        p_values, scores = comstats.t_test(self.input_set, None, {'paired': False, 'equal_variance': False}, True)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_unweighted_t_test_equal_variance(self):
        expected_p_values = [[ 1.        ,  0.00214325,  1.        ,  0.00741902],
                             [ 0.00214325,  1.        ,  0.00214325,  0.43685108],
                             [ 1.        ,  0.00214325,  1.        ,  0.00741902],
                             [ 0.00741902,  0.43685108,  0.00741902,  1.        ]]
        expected_scores = [[ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 3.38132124,  0.        ,  3.38132124,  0.78881064],
                           [ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 2.88675135, -0.78881064,  2.88675135,  0.        ]]
        p_values, scores = comstats.t_test(self.input_set, None, {'paired': False, 'equal_variance': True}, False)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())
    #
    def test_unweighted_t_test_equal_variance_one_sided(self):
        expected_p_values = [[ 0.5       ,  0.00107162,  0.5       ,  0.00370951],
                             [ 0.00107162,  0.5       ,  0.00107162,  0.21842554],
                             [ 0.5       ,  0.00107162,  0.5       ,  0.00370951],
                             [ 0.00370951,  0.21842554,  0.00370951,  0.5       ]]
        expected_scores = [[ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 3.38132124,  0.        ,  3.38132124,  0.78881064],
                           [ 0.        , -3.38132124,  0.        , -2.88675135],
                           [ 2.88675135, -0.78881064,  2.88675135,  0.        ]]
        p_values, scores = comstats.t_test(self.input_set, None, {'paired': False, 'equal_variance': True}, True)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_weighted_t_test(self):
        expected_p_values = [[  1.00000000e+00,   1.42077000e-03,   5.10308380e-01,   7.37402900e-02],
                             [  1.42077000e-03,   1.00000000e+00,   6.57160000e-04,   8.87667500e-02],
                             [  5.10308380e-01,   6.57160000e-04,   1.00000000e+00,   3.35990600e-02],
                             [  7.37402900e-02,   8.87667500e-02,   3.35990600e-02,   1.00000000e+00]]
        expected_scores = [[ 0.        , -3.53992642,  0.66687841, -1.85781692],
                           [ 3.53992642,  0.        ,  3.83253879,  1.76327075],
                           [-0.66687841, -3.83253879,  0.        , -2.23466985],
                           [ 1.85781692, -1.76327075,  2.23466985,  0.        ]]
        p_values, scores = comstats.t_test(self.input_set, self.weights, {'paired': False, 'equal_variance': False})
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_weighted_t_test_one_sided(self):
        expected_p_values = [[  5.00000000e-01,   7.10380000e-04,   2.55154190e-01,   3.68701500e-02],
                             [  7.10380000e-04,   5.00000000e-01,   3.28580000e-04,   4.43833800e-02],
                             [  2.55154190e-01,   3.28580000e-04,   5.00000000e-01,   1.67995300e-02],
                             [  3.68701500e-02,   4.43833800e-02,   1.67995300e-02,   5.00000000e-01]]
        expected_scores = [[ 0.        , -3.53992642,  0.66687841, -1.85781692],
                           [ 3.53992642,  0.        ,  3.83253879,  1.76327075],
                           [-0.66687841, -3.83253879,  0.        , -2.23466985],
                           [ 1.85781692, -1.76327075,  2.23466985,  0.        ]]
        p_values, scores = comstats.t_test(self.input_set, self.weights, {'paired': False, 'equal_variance': False}, True)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_paired_t_test(self):
        expected_p_values = [[     1,  0.00284684,  1.        ,  0.00168927],
                             [ 0.00284684,      1,  0.00946889,  0.4242752 ],
                             [ 1.        ,  0.00946889,      1,  0.01599862],
                             [ 0.00168927,  0.4242752 ,  0.01599862,      1]]
        expected_scores = [[ 0,          -3.60906033, 0.        , -3.87298335],
                           [ 3.60906033, 0,           3.00438276, 0.82305489],
                           [ 0.        , -3.00438276, 0,          -2.73861279],
                           [ 3.87298335, -0.82305489, 2.73861279, 0          ]]
        p_values, scores = comstats.t_test(self.input_set, None, {'paired': True, 'equal_variance': False})
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_paired_t_test_one_sided(self):
        expected_p_values = [[ 0.5       ,  0.00142342,  0.5       ,  0.00084464],
                             [ 0.00142342,  0.5       ,  0.00473445,  0.2121376 ],
                             [ 0.5       ,  0.00473445,  0.5       ,  0.00799931],
                             [ 0.00084464,  0.2121376 ,  0.00799931,  0.5       ]]
        expected_scores = [[ 0.        , -3.60906033,  0.        , -3.87298335],
                           [ 3.60906033,  0.        ,  3.00438276,  0.82305489],
                           [ 0.        , -3.00438276,  0.        , -2.73861279],
                           [ 3.87298335, -0.82305489,  2.73861279,  0.        ]]
        p_values, scores = comstats.t_test(self.input_set, None, {'paired': True, 'equal_variance': False}, True)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_percentage_t_test(self):
        expected_p_values = [[ 1.        ,  0.57861761],
                             [ 0.57861761,  1.        ]]
        expected_scores = [[ 0.        , -0.56195533],
                           [ 0.56195533,  0.        ]]
        p_values, scores = comstats.percentage_t_test(self.percentage_input_set)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_percentage_t_test_one_sided(self):
        expected_p_values = [[ 0.5      ,  0.2893088],
                             [ 0.2893088,  0.5      ]]
        expected_scores = [[ 0.        , -0.56195533],
                           [ 0.56195533,  0.        ]]
        p_values, scores = comstats.percentage_t_test(self.percentage_input_set, None, {'distribution': 't'}, True)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())
    #
    def test_weighted_percentage_t_test_one_sided(self):
        expected_p_values = [[ 0.5      ,  0.4401976],
                             [ 0.4401976,  0.5      ]]
        expected_scores = [[ 0.        , -0.15184861],
                           [ 0.15184861,  0.        ]]
        p_values, scores = comstats.percentage_t_test(self.percentage_input_set, self.percentage_weights, {'distribution': 't'}, True)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())
    #
    def test_weighted_percentage_t_test_z_distribution(self):
        expected_p_values = [[ 1.        ,  0.87930634],
                             [ 0.87930634,  1.        ]]
        expected_scores = [[ 0.        , -0.15184861],
                           [ 0.15184861,  0.        ]]
        p_values, scores = comstats.percentage_t_test(self.percentage_input_set, self.percentage_weights, {'distribution': 'z'})
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_weighted_percentage_t_test_one_sided_z_distribution(self):
        expected_p_values = [[ 0.5       ,  0.43965317],
                             [ 0.43965317,  0.5       ]]
        expected_scores = [[ 0.        , -0.15184861],
                           [ 0.15184861,  0.        ]]
        p_values, scores = comstats.percentage_t_test(self.percentage_input_set, self.percentage_weights, {'distribution': 'z'}, True)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_one_sample_z_test_simple(self):
        expected_p_values = [0.65472085, 0.12282265, 0.49015296, 0.28884437, 0.22067136]
        expected_scores = [0.4472136, 1.5430335, 0.69006556, -1.06066017, 1.22474487]
        p_values, scores = comstats.one_sample_z_test_simple(self.count_set, self.sample_sizes_set, self.population_proportion_set)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())

    def test_one_sample_z_test(self):
        expected_p_values = [0.49015296, 0.49015296]
        expected_scores = [-0.69006556, 0.69006556]
        p_values, scores = comstats.one_sample_z_test(self.binary_sample_input_set, self.population_proportion_scalar)
        self.assertTrue((p_values.round(8) == expected_p_values).all())
        self.assertTrue((scores.round(8) == expected_scores).all())
