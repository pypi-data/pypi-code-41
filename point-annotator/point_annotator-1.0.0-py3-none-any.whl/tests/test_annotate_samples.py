import unittest

import numpy as np
import pandas as pd

from pointannotator.annotate_samples import \
    AnnotateSamples, SCORING_EXP_RATIO, SCORING_MARKERS_SUM, SCORING_LOG_FDR, \
    SCORING_LOG_PVALUE, PFUN_HYPERGEOMETRIC


class TestAnnotateSamples(unittest.TestCase):

    def setUp(self):
        self.markers = pd.DataFrame(
            [["Type 1", "111"], ["Type 1", "112"], ["Type 1", "113"],
             ["Type 1", "114"],
             ["Type 2", "211"], ["Type 2", "212"], ["Type 2", "213"],
             ["Type 2", "214"]],
            columns=["Cell Type", "Gene"])

        genes = ["111", "112", "113", "114", "211", "212", "213", "214"]
        self.data = pd.DataFrame(np.array(
            [[1, 1, 1, 1.1, 0, 0, 0, 0],
             [1, .8, .9, 1, 0, 0, 0, 0],
             [.7, 1.1, 1, 1.2, 0, 0, 0, 0],
             [.8, .7, 1.1, 1, 0, .1, 0, 0],
             [0, 0, 0, 0, 1.05, 1.05, 1.1, 1],
             [0, 0, 0, 0, 1.1, 1.0, 1.05, 1.1],
             [0, 0, 0, 0, 1.05, .9, 1.1, 1.1],
             [0, 0, 0, 0, .9, .9, 1.2, 1]
             ]),
            columns=genes
        )
        self.annotator = AnnotateSamples()

    def test_artificial_data(self):
        annotations = self.annotator.annotate_samples(
            self.data, self.markers, num_genes=15)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

    def test_remove_empty_column(self):
        """
        Type 3 column must be removed here
        """
        markers = pd.DataFrame(
            [["Type 1", "111"], ["Type 1", "112"], ["Type 1", "113"],
             ["Type 1", "114"],
             ["Type 2", "211"], ["Type 2", "212"], ["Type 2", "213"],
             ["Type 2", "214"],
             ["Type 3", "311"], ["Type 3", "312"], ["Type 3", "313"]],
            columns=["Cell Type", "Gene"])

        annotations = self.annotator.annotate_samples(self.data, markers,
                                                      num_genes=20)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

        annotations = self.annotator.annotate_samples(
            self.data, markers, num_genes=20, return_nonzero_annotations=False)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 3)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

    def test_sf(self):
        """
        Test annotations with hypergeom.sf
        """
        annotator = AnnotateSamples()
        annotations = annotator.annotate_samples(
            self.data, self.markers, num_genes=15,
            p_value_fun=PFUN_HYPERGEOMETRIC)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

    def test_two_example(self):
        self.data = self.data.iloc[:2]

        annotations = self.annotator.annotate_samples(self.data, self.markers,
                                                      num_genes=15)
        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))

    def test_select_attributes(self):
        z = self.annotator.mann_whitney_test(self.data)

        self.assertEqual(z.shape, self.data.shape)
        self.assertGreaterEqual(z.iloc[0, 0], 1)
        self.assertGreaterEqual(z.iloc[0, 1], 1)
        self.assertGreaterEqual(z.iloc[0, 3], 1)

    def test_assign_annotations(self):
        z = np.array([
            [1.1, 1.1, 1.1, 1.1, 0, 0, 0, 0],
            [1.1, 1.1, 0, 0, 1.1, 0, 0, 0],
            [1.1, 0, 0, 0, 1.1, 1.1, 0, 0],
            [0, 0, 0, 0, 1.1, 1.1, 1.1, 1.1]
        ])
        z_table = pd.DataFrame(z, columns=self.data.columns)
        attrs = [{"111", "112", "113", "114"}, {"111", "112", "211"},
                 {"211", "212", "111"}, {"211", "212", "213", "214"}]
        exp_ann = np.array([
            [1, 0],
            [1/2, 1/4],
            [1/4, 1/2],
            [0, 1]])
        annotations, fdrs = self.annotator.assign_annotations(
            z_table, self.markers, self.data[:4], num_genes=15)

        self.assertEqual(len(attrs), len(annotations))
        self.assertEqual(len(attrs), len(fdrs))
        self.assertEqual(2, annotations.shape[1])  # only two types in markers
        self.assertEqual(2, fdrs.shape[1])
        np.testing.assert_array_almost_equal(exp_ann, annotations)

        exp_fdrs_smaller = np.array([
            [0.05, 2],
            [2, 2],
            [2, 2],
            [2, 0.05]])

        np.testing.assert_array_less(fdrs, exp_fdrs_smaller)

    def test_scoring(self):
        # scoring SCORING_EXP_RATIO
        annotations = self.annotator.annotate_samples(
            self.data, self.markers, num_genes=15, scoring=SCORING_EXP_RATIO)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data
        self.assertGreater(np.nansum(annotations), 0)
        self.assertLessEqual(np.nanmax(annotations), 1)
        self.assertGreaterEqual(np.nanmin(annotations), 0)

        # scoring SCORING_MARKERS_SUM
        annotations = self.annotator.annotate_samples(
            self.data, self.markers, num_genes=15, scoring=SCORING_MARKERS_SUM)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data

        # based on provided data it should match
        # the third row is skipped, since it is special
        self.assertEqual(annotations.iloc[0, 0], self.data.iloc[0].sum())
        self.assertEqual(annotations.iloc[5, 1], self.data.iloc[5].sum())

        # scoring SCORING_LOG_FDR
        annotations = self.annotator.annotate_samples(
            self.data, self.markers, num_genes=15, scoring=SCORING_LOG_FDR)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data

        # scoring SCORING_LOG_PVALUE
        annotations = self.annotator.annotate_samples(
            self.data, self.markers, num_genes=15, scoring=SCORING_LOG_PVALUE)

        self.assertEqual(type(annotations), pd.DataFrame)
        self.assertEqual(len(annotations), len(self.data))
        self.assertEqual(len(annotations.iloc[0]), 2)  # two types in the data

    def test_log_cpm(self):
        norm_data = self.annotator.log_cpm(self.data)
        self.assertTupleEqual(self.data.shape, norm_data.shape)

    def test_markers_wrong_type(self):
        self.markers["Gene"] = pd.to_numeric(self.markers["Gene"])
        self.assertRaises(AssertionError, self.annotator.annotate_samples,
                          self.data, self.markers, num_genes=15)

    def test_keep_dataframe_index(self):
        self.data.index = np.random.randint(0, 16, len(self.data))
        data_index = self.data.index.values.tolist()
        annotations = self.annotator.annotate_samples(
            self.data, self.markers, num_genes=15, scoring=SCORING_MARKERS_SUM)
        self.assertListEqual(data_index, annotations.index.values.tolist())
