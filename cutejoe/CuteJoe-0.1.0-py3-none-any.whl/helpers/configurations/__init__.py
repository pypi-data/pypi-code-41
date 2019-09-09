from .base import ChangelogConfigFactory, Config  # noqa
from .config_v1 import ChangelogConfigV1


ChangelogConfigFactory().register(1, ChangelogConfigV1)
