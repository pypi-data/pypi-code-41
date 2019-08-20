import pandas as pd

from .views import _sort, _tabview


class Table(pd.DataFrame):
    """
    A dataframe with numerical datapoints
    """

    _internal_names = pd.DataFrame._internal_names + ["reference"]
    _internal_names_set = set(_internal_names)

    _metadata = ["reference", "path", "name"]

    def __init__(self, data, reference=None, **kwargs):
        super().__init__(data, **kwargs)
        self.reference = reference

    @property
    def _constructor(self):
        return Table

    def view(self, *args, **kwargs):
        return _tabview(self, self.reference, *args, **kwargs)

    def sort(self, by="total", keep_stats=False, remove_above_p=False):
        """
        Sort this table

        by: (total/infreq), (increase/decrease), (static/turbulent), (name/inverse)
        keep_stats: keep the info generated by scipy linear regression
        remove_above_p can be used to drop items whose p value is too high
        """
        return _sort(self, by=by, keep_stats=keep_stats, remove_above_p=remove_above_p)

    def plot(self, *args, **kwargs):
        """
        Visualise this table
        """
        pass

    def relative(self, denom=None):
        """
        Give a relative frequency version of this table
        """
        from .dataset import Dataset

        if denom is True or denom is None:
            denom = self
        if isinstance(denom, Dataset):
            denom = denom.table(subcorpora=list(self.index.names))
        if not isinstance(denom, pd.Series):
            denom = denom.sum(axis=1)
        return (self.T * 100.0 / denom).T

    def square(self, n=10):
        """
        Our version of .head() restricts both rows and columns
        """
        return self.iloc[:n, :n]

    def site(self, title=None, kind="bar", **kwargs):
        from .dashview import DashSite

        title = title or getattr(self, "name", None)
        site = DashSite(title)
        height, width = self.shape
        if height > 100 or width > 100:
            warn = f"Warning: shape of data is large ({self.shape}). Performance may be slow."
            print(warn)
        dataset = self.to_frame() if isinstance(self, pd.Series) else self
        site.add(kind, dataset)
        site.add("datatable", dataset)
        site.run()
        return site
