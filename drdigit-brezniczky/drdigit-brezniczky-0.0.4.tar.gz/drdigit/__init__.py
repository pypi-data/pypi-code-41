from . import (
    digit_entropy_distribution, digit_correlations,
    twin_digits, digit_filtering,
    fingerprint_plots, digit_distribution_charts,
)
from joblib import Memory

# TODO: utilize a default such as "./digit_correlations_cache"


__all__ = (
    "twin_digits",
    "digit_correlations",
    "digit_entropy_distribution",
    "fingerprint_plots",
    "digit_distribution_charts",
)

_mem = None


def set_option(physical_cache_path=None):
    """
    Set global options to the package.

    :param physical_cache_path: Caching through python interpreter restarts
        can save a lot of time. This option allows on-disk caching when the
        path is specified. The default, None, sticks with in-memory caching.

        Kaggle kernels "seemed to like" on disk caching as long as I didn't
        try to commit the notebook. Then things ended up with a Code: 0 error
        failing the publishing attempt.

    :return: None
    """
    if physical_cache_path is not None:
        _mem = Memory(physical_cache_path, verbose=0)
        digit_correlations.cached_get_digit_correlation_data = \
            _mem.cache(digit_correlations.uncached_get_digit_correlation_data)
        digit_entropy_distribution.cached_generate_sample = \
            _mem.cache(digit_entropy_distribution.uncached_generate_sample)
    else:
        digit_correlations.cached = \
            digit_correlations.cached_get_digit_correlation_data
        digit_entropy_distribution.cached_generate_sample = \
            digit_entropy_distribution.cached_generate_sample


def clear_physical_cache():
    """
    Clear the on-disk cache if on-disk caching is enabled, otherwise does
    nothing.

    :return: None
    """
    if _mem is not None:
        _mem.clear()
