import os
from git import Repo
from git.exc import GitCommandError


class CivisGit():
    def __init__(self, repo_url=None, repo_mount_path=None, git_repo_ref=None):
        self.repo_url = os.environ.get('GIT_REPO_URL', repo_url)
        self.git_repo_mount_path = repo_mount_path if repo_mount_path else os.path.expanduser(os.path.join('~', 'work'))
        self.git_repo_ref = os.environ.get('GIT_REPO_REF', git_repo_ref)

    def repo(self):
        return Repo(self.git_repo_mount_path)

    def clone_repository(self):
        try:
            repo = Repo.clone_from(self.repo_url, self.git_repo_mount_path)
            repo.git.checkout(self.git_repo_ref)
        except GitCommandError as e:
            raise CivisGitError(e)

    def is_git_enabled(self):
        return self.repo_url is not None

    def has_uncommitted_changes(self):
        try:
            repo = self.repo()
            staged_files = len(repo.index.diff("HEAD")) > 0
            changed_files = len(repo.index.diff(None)) > 0
            return changed_files or staged_files

        except GitCommandError as e:
            raise CivisGitError(e)


class CivisGitError(Exception):
    """
    General error raised whenever a Git related error comes up
    """
