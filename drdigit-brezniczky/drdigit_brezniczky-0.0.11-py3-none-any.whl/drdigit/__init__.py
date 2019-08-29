from . import (
    digit_entropy_distribution, digit_correlations,
    twin_digits, digit_filtering,
    fingerprint_plots, digit_distribution_charts,
)
from .digit_correlations import (
    digit_correlation_cdf, equality_rel_freq, digit_equality_prob_cdf,
    correlation_prob_coeff_df, equality_prob_coeff_df, equality_prob_vector,
    get_col_mean_prob, get_matrix_mean_prob,
)
from .digit_entropy_distribution import (
    get_entropy, get_entr_cdf_fun, prob_of_entr, LogLikelihoodDigitGroupEntropyTest,
    LodigeTest,
)
from .digit_filtering import get_feasible_groups, get_feasible_rows
from .scoring import get_group_scores
from .fingerprint_plots import (plot_fingerprint, plot_animated_fingerprints,
                                plot_explanatory_fingerprint_responses)
from .entropy_plots import plot_entropy_distribution


from joblib import Memory


DEFAULT_CACHE_PATH = "./.drdigit_cache"


__all__ = (
    "digit_correlation_cdf",
    "equality_rel_freq",
    "digit_equality_prob_cdf",
    "correlation_prob_coeff_df",
    "equality_prob_coeff_df",
    "equality_prob_vector",
    "get_col_mean_prob",
    "get_matrix_mean_prob",
    "get_entropy",
    "get_entr_cdf_fun",
    "prob_of_entr",
    "LogLikelihoodDigitGroupEntropyTest",
    "LodigeTest",
    "get_feasible_groups",
    "get_feasible_rows",
    "get_group_scores"
    "plot_fingerprint",
    "plot_animated_fingerprints",
    "plot_explanatory_fingerprint_responses",
)

_mem = None


def set_option(physical_cache_path: str=None) -> None:
    """
    Set global options to the package.

    :param physical_cache_path: Caching across Python interpreter sessions
        can save a lot of time. This option allows on-disk caching when the
        path is specified.

        Specifying an empty string ("") switches disk-caching off explicitly.
        Use "." to specify the current working directory instead.
        Kaggle kernels "seemed to like" on disk caching as long as I didn't
        try to commit the notebook. Then things ended up with a Code: 0 error
        failing the publishing attempt. It may be the most convenient there to
        comment out a set_option("") while experimenting, and to uncomment it
        just before committing the kernel.

        Leaving it at the default of None leaves the options unchanged.
        (There's likely more to come.)
    :return: None
    """
    if physical_cache_path is not None:
        global _mem

        if physical_cache_path != "":
            _mem = Memory(physical_cache_path, verbose=0)
            digit_correlations._cached_get_digit_correlation_data = \
                _mem.cache(digit_correlations._uncached_get_digit_correlation_data)
            digit_entropy_distribution.cached_generate_sample = \
                _mem.cache(digit_entropy_distribution._uncached_generate_sample)
        else:
            _mem = None
            digit_correlations.cached = \
                digit_correlations._lru_cached_get_digit_correlation_data
            digit_entropy_distribution.cached_generate_sample = \
                digit_entropy_distribution._lru_cached_generate_sample


def clear_physical_cache() -> None:
    """
    Clear the on-disk cache if on-disk caching is enabled, otherwise does
    nothing.

    :return: None
    """
    if _mem is not None:
        _mem.clear()


set_option(physical_cache_path=DEFAULT_CACHE_PATH)
