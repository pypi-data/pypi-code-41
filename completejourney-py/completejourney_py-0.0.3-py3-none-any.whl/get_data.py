import pandas as pd
from pkg_resources import resource_filename

def get_data(which=None):
    """Returns datasets from the complete journey set.

    Args:
        which: which dataset(s) to read. Can be a string for a single dataset,
            a sequence of strings for multiple datsets, or left blank for all
            available datasets.
    Returns:
        A dictionary mapping dataset name to pandas data frames.
    """

    sources = ["campaign_descriptions",
               "coupons",
               "promotions",
               "campaigns",
               "demographics",
               "transactions",
               "coupon_redemptions",
               "products"]

    if which is None:
        which = sources
    elif isinstance(which, str):
        which = [which]
    else:
        which = list(which)

    return dict(
        map(lambda src: (src, pd.read_parquet(resource_filename("completejourney_py", f"data/{src}.parquet"))),
            which))
