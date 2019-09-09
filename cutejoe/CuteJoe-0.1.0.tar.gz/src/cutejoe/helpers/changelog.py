import re
from datetime import date
from typing import Set, List

from .configurations import ChangelogConfigV1
from .utils import get_unreleased_commits, get_project_url, get_last_tag


class Changelog:
    COMMITS_PATTERN = r"^'?(?:\s*(?P<label>\w+)\s*:)?\s*(?P<message>.*?)\s*'?\r?$"

    def __init__(self, config: ChangelogConfigV1):
        self.config = config

    @property
    def branch(self):
        return f"release/{self.tag}"

    @property
    def content(self) -> List[str]:
        field_name = '_content'

        if not hasattr(self, field_name):
            commits = self._get_grouped_commits()
            content = []

            for kind, kind_commits in commits.items():
                title = self.config.get_title(kind)

                content.append(f"### {title}\n")
                content.extend(f"- {c}\n" for c in kind_commits)
                content.append("\n")

            url = get_project_url()

            if url:
                last_tag = get_last_tag()
                content.append(f"[{self.tag}]: {url}/compare/{last_tag}..{self.tag}\n")

            setattr(self, field_name, content)

        return getattr(self, field_name)

    @property
    def file_path(self):
        today = date.today()
        return f"{self.config.folder}/[{self.tag}] - {today}.md"

    @property
    def tag(self) -> str:
        field_name = '_tag'

        if not hasattr(self, field_name):
            last_tag = get_last_tag()
            tag_increment_position = self._get_tag_increment_position()

            new_tag = list(map(int, last_tag.lstrip("v").split(".")))
            new_tag[tag_increment_position] += 1

            next_position = tag_increment_position + 1
            new_tag[next_position:] = [0] * len(new_tag[next_position:])

            new_tag = "v" + ".".join(map(str, new_tag))

            setattr(self, field_name, new_tag)

        return getattr(self, field_name)

    def _get_tag_increment_position(self) -> int:
        commit_kinds = self._get_kinds()
        commits_versions = [self.config.get_version(k) for k in commit_kinds]

        if "major" in commits_versions:
            return 0  # major
        elif "minor" in commits_versions:
            return 1  # minor

        return 2  # patch

    def _get_kinds(self) -> Set[str]:
        commits = self._get_grouped_commits()
        return set(commits.keys())

    def _get_grouped_commits(self):
        raw_commits = get_unreleased_commits(self.config.start, self.config.end)
        commit_matches = re.finditer(self.COMMITS_PATTERN, raw_commits, re.MULTILINE)

        commits = {}
        for commit_match in commit_matches:
            commit_label = commit_match.group("label")
            commit_message = commit_match.group("message")
            commit_kind = self.config.get_kind(commit_label)

            if not commit_message:
                continue  # ignore empty message

            commits.setdefault(commit_kind, [])
            commits[commit_kind].append(commit_message)

        return commits
