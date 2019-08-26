import enum

from py_jaeger_tracing.patches.requests import patch_requests
from py_jaeger_tracing.patches.boto3 import patch_boto3


class TracingPatch(enum.Enum):
    REQUESTS = patch_requests
    BOTO_3 = patch_boto3


class TracingPatcher:
    @classmethod
    def apply_patches(cls, patches):
        for patch in patches:
            patch()
