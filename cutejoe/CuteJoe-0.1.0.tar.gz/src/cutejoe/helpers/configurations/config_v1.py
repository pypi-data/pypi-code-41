from .base import BaseChangelogConfig


class ChangelogConfigV1(BaseChangelogConfig):

    def __init__(self, **kwargs) -> None:
        self.folder = kwargs.get("folder", "changelogs")
        self.start = kwargs.get("start", "master")
        self.end = kwargs.get("end", "HEAD")
        self.default_title = kwargs.get("default_title", "Uncategorized")
        self.kinds = kwargs.get("kinds", {})

    def get_title(self, kind=None):
        return self.kinds.get(kind, {}).get("title") or self.default_title

    def get_version(self, kind=None):
        return self.kinds.get(kind, {}).get("version")

    def get_kind(self, label=None):
        # TODO Improve me, please
        key = [key for key, value in self.kinds.items() if label in value.get("labels")]
        return key[0] if key else None
