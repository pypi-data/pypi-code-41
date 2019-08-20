from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("py-figure-eight").version
except DistributionNotFound:
    pass


from .figure_eight import FigureEightClient, FigureEightJob
