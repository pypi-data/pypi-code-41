import numpy as np
import pandas as pd
import numpy.random as rnd
from scipy import stats
from functools import lru_cache


def uncached_get_digit_correlation_data(n_digits, seed=1234,
                                        n_iterations=10000):
    corrs = []
    rnd.seed(seed)
    for i in range(n_iterations):
        digits_1 = rnd.choice(range(10), n_digits)
        digits_2 = rnd.choice(range(10), n_digits)
        act_corr = np.corrcoef(digits_1, digits_2)
        corrs.append(act_corr[1, 0])

    corrs = sorted(corrs)
    return corrs


# failed to say lru_cache(..., 1000) - seems like as opposed to
# joblib.Memory.cache(), it just doesn't work that way
@lru_cache()
def lru_cached_get_digit_correlation_data(*args, **kwargs):
    return uncached_get_digit_correlation_data(*args, **kwargs)


cached_get_digit_correlation_data = lru_cached_get_digit_correlation_data


@lru_cache(1000)
def digit_correlation_cdf(n_digits, seed=1234, n_iterations=10000):
    """
    Get the CDF (actually, survival function) of digit correlation values
    between two random uniformly distributed base 10 digit sequences, that is,
    the function

    Remark: this is not really used anywhere, was an early attempt.
    Can it still be useful later?

    f(x)=P(corr(A, B) >= x)

    where A and B are the n_digits long digit sequences.

    The survival function was chosen as it probably makes more sense in the
    digit doctoring context.

    :param n_digits: number of digits
    :param seed: random seed to use for the MC simulation taking place that
        leads to the values. set for reproducibility but can also be used to
        examine stability of the results or their convergence.
    :param n_iterations: number of iterations to use for the MC simulation.
    :return: "CDF" function.
    """

    # a small but efficient tribute to The Corrs :)
    corrs = cached_get_digit_correlation_data(n_digits, seed, n_iterations)

    def cdf(x):
        return np.digitize(x, corrs, right=False) / len(corrs)

    cdf.iterations = n_iterations
    cdf.max_x = corrs[-1]
    cdf.min_x = corrs[0]
    return cdf


def equality_rel_freq(a1: np.array, a2: np.array):
    ans = (a1 == a2).mean()
    return ans


@lru_cache(1000)
def digit_equality_prob_cdf(n):
    """
    Return a function telling the probability of at least k digits being equal
    out of n pairs, described as the relative frequency k/n.

    :param n: number of 10 base digit pairs that were examined and assumed
        uniformly distributed
    :return: function f(x) telling the probability from the single relative
        frequency parameter x = k / n, k being the number of experienced
        equalities.
    """
    inner_cdf = stats.binom(n, 0.1).cdf

    def cdf(rel_freq):
        # TODO: possibly do not operate on rel_freq... inaccurate values ~ waste
        return 1 - inner_cdf(int(round(rel_freq * n - 1)))

    return cdf


def correlation_prob_coeff_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a data frame containing the probabilities of the (Pearson)
    correlations being at least that high between the columns, assuming a
    uniform digit distribution:

    output[name_col1, name_col2] = P(corr(col1, col2) <= X)

    X being the correlation as a r.v.

    :param df: Source data frame with columns to correlate.
    :return: The output cross correlation probability matrix.
    """
    ans_df = pd.DataFrame(columns=df.columns)
    ans_df["row_name"] = df.columns
    ans_df.set_index(["row_name"], inplace=True)

    cdf = digit_correlation_cdf(len(df))
    for row in df.columns:
        for col in df.columns:
            corr = np.corrcoef(df[row].values, df[col].values)[0, 1]
            try:
                ans_df.loc[row][col] = 1 - cdf(corr)
            except Exception as ex:
                import ipdb;
                ipdb.set_trace()
                print(ex)
    return ans_df


def equality_prob_coeff_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a data frame containing the for each column pair col1, col2 the
    probability of observing as high a number of equal digits as there
    happen to be (number of index i's for which col1[i] == col2[i]) for the
    columns of a data frame:

    output[name_col1, name_col2] = P(sum(1_{col1 = col2}) >= X)

    X being the correlation r.v.

    :param df: Source data frame with columns to correlate.
    :return: The output cross correlation probability matrix.
    """
    ans_df = pd.DataFrame(columns=df.columns)
    ans_df["row_name"] = df.columns
    ans_df.set_index(["row_name"], inplace=True)

    cdf = digit_equality_prob_cdf(len(df))
    for row in df.columns:
        for col in df.columns:
            prob = equality_rel_freq(df[row].values, df[col].values)
            try:
                ans_df.loc[row][col] = cdf(prob)
            except Exception as ex:
                import ipdb; ipdb.set_trace()
                print(ex)
                raise
    return ans_df


def equality_prob_vector(base_column: np.array,
                         indep_columns: np.array) -> np.array:
    """
    Find out the probability of at least the number of equal digit pairs
    observed in the pairs formed from the base column and the indep. columns.

    :param base_column: base column to consider
    :param indep_columns: independent columns
    :return: a numpy array of len(indep_columns) values containing the
        digit equality probabilities for each pair that could be formed.
    """

    cdf = digit_equality_prob_cdf(len(base_column))
    ans = [
        cdf(equality_rel_freq(base_column, indep_column))
        for indep_column in indep_columns
    ]
    return np.array(ans)


def get_col_mean_prob(df, col_name) -> float:
    """ Return an average probability (geometric mean probability) generated
        from the contents of the column, except for the "diagonal" value.

        Diagonal values are zero in correlation/equality prob. matrices."""
    s = np.exp(np.mean(np.log(
        df[df.index != col_name][col_name].values.astype(float)
    )))
    return s


def get_matrix_mean_prob(df: pd.DataFrame) -> float:
    """ Return an average probability (geometric mean probability) generated
        from the contents of the matrix described as a data frame, except for
        the "diagonal" values.

        Diagonal values are zero in correlation/equality prob. matrices.
    """
    ans = np.exp(np.mean([np.log(df[r][c])
                           for r in df.index
                           for c in df.columns if r != c]))
    return ans
