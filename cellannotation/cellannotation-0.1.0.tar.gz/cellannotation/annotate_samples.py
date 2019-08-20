import numpy as np
import pandas as pd

from scipy.stats.mstats import rankdata
from scipy.stats import hypergeom, binom

from cellannotation.utils import FDR

SCORING_EXP_RATIO = "scoring_exp_ratio"
SCORING_MARKERS_SUM = "scoring_sum_of_expressed_markers"
SCORING_LOG_FDR = "scoring_log_fdr"
SCORING_LOG_PVALUE = "scoring_log_p_value"

PFUN_BINOMIAL = "binom"
PFUN_HYPERGEOMETRIC = "hypergeom"


class ScoringNotImplemented(Exception):
    pass


class AnnotateSamples:
    """
    AnnotateSamples is class used for the annotation of data items with the
    labels (e.g. Cell Types) Mann-Whitney U test for selecting important values
    and the Hyper-geometric for assigning the labels.

    Example for full annotation:

    >>> gene_expressions_df = pd.read_csv("data/DC_expMatrix_DCnMono.csv.gz",
    ...                                   compression='gzip')
    >>> marker_genes_df = pd.read_csv("data/panglao_gene_markers.csv.gz",
    ...                               compression="gzip")
    >>> # rename genes column and filter human markers
    >>> marker_genes_df = marker_genes_df.rename(columns={'Name': 'Gene'})
    >>> marker_genes_df = marker_genes_df[
    ...     marker_genes_df["Organism"] == "Human"]
    >>>
    >>> annotations = AnnotateSamples.annotate_samples(
    ...     gene_expressions_df, marker_genes_df, num_genes=60000,
    ...     p_threshold=0.05)

    Example for full manual annotation. Here annotation is split in three
    phases. We assume that data are already loaded.

    >>> z = AnnotateSamples.mann_whitney_test(gene_expressions_df)
    >>> scores, p_val = AnnotateSamples.assign_annotations(
    ...     z, marker_genes_df, gene_expressions_df, num_genes=60000)
    >>> scores = AnnotateSamples.filter_annotations(
    ...     scores, p_val, p_threshold=0.05)

    Attributes
    ----------

    """
    @staticmethod
    def log_cpm(data):
        """
        Function normalizes data with CPM methods and normalize them.

        Parameters
        ----------
        data : pd.DataFrame
            Non-normalized gene expression data.

        Returns
        -------
        Orange.data.Table
            Normalized gene expression data
        """
        norm_data = np.log(1 + AnnotateSamples._cpm(data))
        return norm_data

    @staticmethod
    def _cpm(data):
        """
        This function normalizes data with CPM methods.

        Parameters
        ----------
        data : array_like
            Numpy array with data. Columns are genes, rows are cells.
        """
        return data / np.sum(data, axis=1)[:, None] * 1e6

    @staticmethod
    def _ranks(data):
        """
        This function computes ranks for data in the table along axis=0.

        Parameters
        ----------
        data : np.ndarray
            Array of data to be ranked

        Returns
        -------
        np.ndarray
            Table of data ranks
        """
        x_len = data.shape[0]
        x_mask = data.sum(axis=0) > 0

        # create a matrix of ranges - init with average rank
        # for columns without nonzero expressions
        data_ge_ranked = np.ones(data.shape) * (1 + data.shape[0]) / 2

        # compute ranks only for nonzero columns
        for i in np.where(x_mask)[0]:
            mask = data[:, i] > 0
            col = np.ones(x_len) * (1 + (x_len - mask.sum())) / 2
            col[mask] = rankdata(data[mask, i]) + (x_len - mask.sum())
            data_ge_ranked[:, i] = col
        return data_ge_ranked

    @staticmethod
    def mann_whitney_test(data):
        """
        Compute z values with test Mann-Whitney U test.

        Parameters
        ----------
        data : pd.DataFrame
            Tabular data with gene expressions

        Returns
        -------
        pd.DataFrame
            Z-value for each item.
        """
        if len(data) <= 1:
            return None

        # rank data
        data_ge_ranked = AnnotateSamples._ranks(data.values)

        # compute U, mu, sigma
        n = data_ge_ranked.shape[0]
        n2 = n - 1
        u = data_ge_ranked - 1
        mu = n2 / 2
        sigma = np.zeros(data_ge_ranked.shape[1])

        for i in range(data_ge_ranked.shape[1]):
            _, counts = np.unique(data_ge_ranked[:, i], return_counts=True)
            sigma[i] = np.sqrt(
                1 * n2 / 12 * ((n + 1) - np.sum((counts ** 3 - counts)) /
                               (n * (n - 1))))

        # compute z
        z = (u - mu) / (sigma + 1e-16)

        # pack z values to pandas dataframe
        z_dataframe = pd.DataFrame(z, columns=data.columns)
        return z_dataframe

    @staticmethod
    def _reorder_matrix(matrix, genes_order):
        """
        Function reorder the columns of the array to fit to the genes_order

        Parameters
        ----------
        matrix : pd.DataFrame
            Tabular data tha needs to be reordered
        genes_order : list
            Desired genes order

        Returns
        ------
        np.ndarray
            Reordered array.
        """
        current_order = np.array(matrix.columns.values)
        values = matrix.values
        genes_order = np.array(genes_order)

        xsorted = np.argsort(genes_order)
        ypos = np.searchsorted(genes_order[xsorted], current_order)
        indices = xsorted[ypos]  # index which tell where should be the column

        reordered_values = np.zeros((values.shape[0], len(genes_order)))
        for i_curr, i_dest in enumerate(indices):
            reordered_values[:, i_dest] = values[:, i_curr]

        return reordered_values

    @staticmethod
    def _select_attributes(z, genes_order, z_threshold=1):
        """
        Function selects "over"-expressed attributes for items based on z
        values. It also reorder the matrix columns.

        Parameters
        ----------
        z : pd.Dataframe
            Tabular data z values for each item in the table
        genes_order : list
            Desired genes order
        z_threshold : float
            The threshold for selecting the attribute. For each item the
            attributes with z-value above this value are selected.

        Returns
        -------
        np.ndarray
            Reordered and thresholded z-values/
        """
        reordered_z = AnnotateSamples._reorder_matrix(z, genes_order)

        return reordered_z > z_threshold

    @staticmethod
    def _group_marker_attributes(markers, genes_order):
        """
        Function transforms annotations to
        matrix with size (genes_order x types)
        """
        types = sorted(list(set(markers.loc[:, "Cell Type"].values)))
        genes_celltypes = np.zeros((len(genes_order), len(types)))

        for _, m in markers.iterrows():
            g = m["Gene"]
            m = m["Cell Type"]
            if g is not None:
                genes_celltypes[genes_order.index(g), types.index(m)] = 1

        return genes_celltypes, types

    @staticmethod
    def _score(scoring_type, p_values, fdrs, data, M, x, m, genes_order):
        if scoring_type == SCORING_MARKERS_SUM:
            return AnnotateSamples._reorder_matrix(data, genes_order).dot(M)
        elif scoring_type == SCORING_EXP_RATIO:
            return x / m
        elif scoring_type == SCORING_LOG_FDR:
            return -np.log(fdrs)
        elif scoring_type == SCORING_LOG_PVALUE:
            return -np.log(p_values)
        else:
            raise ScoringNotImplemented()

    @staticmethod
    def assign_annotations(z_values, available_annotations, data, num_genes,
                           z_threshold=1,
                           p_value_fun=PFUN_BINOMIAL,
                           scoring=SCORING_EXP_RATIO):
        """
        The function gets a set of attributes (e.g. genes) for each cell and
        attributes for each annotation. It returns the annotations significant
        for each cell.

        Parameters
        ----------
        z_values : pd.DataFrame
            DataFrame which show z values for each item
        available_annotations : pd.DataFrame
            Available annotations (e.g. cell types), this data frame has
            two columns `Genes` and `Cell Types`.
        num_genes : int
            Number of genes that the organism has.
        z_threshold : float
            The threshold for selecting the attribute. For each item the
            attributes with z-value above this value are selected.
        p_value_fun : str, optional (defaults: TEST_BINOMIAL)
            A function that calculates p-value. It can be either
            PFUN_BINOMIAL that uses binom.sf or
            PFUN_HYPERGEOMETRIC that uses hypergeom.sf.
        data : pd.DataFrame
            Tabular data with gene expressions - we need that to compute scores.
        scoring : str, optional (default=SCORING_EXP_RATIO)
            Type of scoring

        Returns
        -------
        pd.DataFrame
            Annotation probabilities
        pd.DataFrame
            Annotation fdrs
        """
        assert available_annotations["Gene"].dtype == object, \
            "The type of genes column must be string/object"
        assert available_annotations["Cell Type"].dtype == object, \
            "The type of genes column must be string/object"

        # select function for p-value
        if p_value_fun == PFUN_HYPERGEOMETRIC:
            p_fun = lambda x, N, m, k: hypergeom.sf(x, N, m, k)
        else:
            p_fun = lambda x, N, m, k: binom.sf(x, k, m / N)

        # make an attributes order
        genes_data = z_values.columns.values
        genes_celltypes = available_annotations["Gene"].values
        genes_order = list(set(genes_data) | set(genes_celltypes))

        # get marker genes matrix M
        M, annotations = AnnotateSamples._group_marker_attributes(
            available_annotations, genes_order)

        Z = AnnotateSamples._select_attributes(
            z_values, genes_order, z_threshold)

        x = Z.dot(M)
        k = np.repeat(Z.sum(axis=1).reshape(-1, 1), x.shape[1], axis=1)
        m = np.repeat(M.sum(axis=0).reshape(1, -1), x.shape[0], axis=0)

        p_values = p_fun(x - 1, num_genes, m, k)

        fdrs = np.zeros(p_values.shape)
        for i, row in enumerate(p_values):
            fdrs[i] = np.array(FDR(row.tolist()))

        scores = AnnotateSamples._score(
            scoring, p_values, fdrs, data, M, x, m, genes_order)

        scores_table = pd.DataFrame(scores, columns=annotations)
        fdrs_table = pd.DataFrame(fdrs, columns=annotations)

        return scores_table, fdrs_table

    @staticmethod
    def filter_annotations(scores, p_values, return_nonzero_annotations=True,
                           p_threshold=0.05):
        """
        This function filters the probabilities on places that do not reach the
        threshold for p-value and filter zero columns
        return_nonzero_annotations is True.

        Parameters
        ----------
        scores : pd.DataFrame
            Scores for each annotations for each cell
        p_values : pd.DataFrame
            p-value scores for annotations for each cell
        return_nonzero_annotations : bool
            Flag that enables filtering the non-zero columns.
        p_threshold : float
            A threshold for accepting the annotations. Annotations that has FDR
            value bellow this threshold are used.

        Returns
        -------
        pd.Dataframe
            Filtered scores for each annotations for each cell
        """
        scores = scores.copy()  # do not want to edit values inplace
        scores[p_values > p_threshold] = np.nan

        if return_nonzero_annotations:
            col_not_empty = ~np.isnan(scores).all(axis=0)
            scores = scores.loc[:, col_not_empty]
        return scores

    @staticmethod
    def annotate_samples(data, available_annotations, num_genes,
                         return_nonzero_annotations=True, p_threshold=0.05,
                         p_value_fun=PFUN_BINOMIAL, z_threshold=1,
                         scoring=SCORING_EXP_RATIO, normalize=False):
        """
        Function marks the data with annotations that are provided. This
        function implements the complete functionality. First select genes,
        then annotate them and filter them.

        Parameters
        ----------
        data : pd.DataFrame
            Tabular data
        available_annotations : pd.DataFrame
            Available annotations (e.g. cell types)
        num_genes : int
            Number of genes that the organism has.
        return_nonzero_annotations : bool, optional (default=True)
            If true return scores for only annotations present in at least one
            sample.
        p_threshold : float
            A threshold for accepting the annotations. Annotations that has FDR
            value bellow this threshold are used.
        p_value_fun : str, optional (defaults: TEST_BINOMIAL)
            A function that calculates p-value. It can be either
            PFUN_BINOMIAL that uses statistics.Binomial().p_value or
            PFUN_HYPERGEOMETRIC that uses hypergeom.sf.
        z_threshold : float
            The threshold for selecting the attribute. For each item the
            attributes with z-value above this value are selected.
        scoring : str, optional (default = SCORING_EXP_RATIO)
            Type of scoring
        normalize : bool, optional (default = False)
            This variable tells whether to normalize data or not.

        Returns
        -------
        pd.DataFrame
            Cell type most important for each cell.
        """
        assert len(data) > 1, "At least two data items are required for " \
                              "method to work."

        if normalize:
            data = AnnotateSamples.log_cpm(data)

        z = AnnotateSamples.mann_whitney_test(
            data)

        annotation_probs, annotation_fdrs = AnnotateSamples.assign_annotations(
            z, available_annotations, data, num_genes, z_threshold=z_threshold,
            p_value_fun=p_value_fun, scoring=scoring)

        annotation_probs = AnnotateSamples.filter_annotations(
            annotation_probs, annotation_fdrs, return_nonzero_annotations,
            p_threshold
        )

        return annotation_probs
