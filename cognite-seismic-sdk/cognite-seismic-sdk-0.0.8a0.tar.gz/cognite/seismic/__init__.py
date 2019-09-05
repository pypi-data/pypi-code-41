import os
import sys

from cognite.seismic._api_client import CogniteSeismicClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "protocompiled")))


__version__ = "0.0.8a"
