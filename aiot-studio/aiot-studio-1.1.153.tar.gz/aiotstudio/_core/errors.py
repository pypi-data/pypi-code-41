from __future__ import absolute_import

import warnings
warnings.warn("Module aiotstudio._core.errors is deprecated and will be removed in future versions. Please use aiotstudio.errors instead.")

from aiotstudio.errors import (
    AiotStudioError,
    UnauthorizedError,
    ConfigurationError,
    FeatureUnavailableError,
    BlobStoreError,
    BlobStoreTimeoutError,
    BlobStoreBucketNotFound,
    BlobStoreObjectNotFound,
    SearchError as RestitutionError,
    SearchTimeoutError as RestitutionTimeoutError,
    SearchResultError as RestitutionResultError
)
