import re
import shutil
import subprocess
import logging

from typing import Optional
from git_dependency_python.version_resolver import VersionResolver

logr = logging.getLogger(__name__)


class GitDependency:
    """
    Class describing a git dependency and methods used on it.
    """

    def __init__(self, project_name, version_to_resolve, git_subpath, environment='dev'):
        # type: (str, str, str, str) -> None
        """
        Constructor function.

        :param project_name: Name of your project.
        :param version_to_resolve: Unresolved version of dependency, e.g. "5.*.*"
        :param git_subpath: Path to git repository of your dependency.
        :param environment: Specified either production or development environment.

        :return: No return.
        """
        self.environment = environment
        assert environment in ['dev', 'prod'], 'Bad environment.'

        self.git_subpath = git_subpath
        assert self.git_subpath, 'Git subpath not provided.'

        self.version_to_resolve = version_to_resolve
        assert self.version_to_resolve, 'Version to resolve not provided.'

        self.project_name = project_name
        assert self.project_name, 'Project name not provided.'

        # Other properties.
        self.remote_git_tags = []
        self.resolved_version = ''
        self.src_cloned_path = '/tmp/{}/install/src'.format(self.project_name)

    def __str__(self):
        return '{}-{} ({})'.format(self.project_name, self.version_to_resolve, self.environment)

    def __repr__(self):
        return str(self)

    def fetch_remote_tags(self):
        # type: () -> subprocess.Popen
        """
        Initiates a process for tags fetching.

        :return: Process instance which returns a git-formatted api response for remote tags.
        """
        command = ['git', 'ls-remote', '--tags', 'ssh://git@bitbucket.org/{}.git'.format(self.git_subpath)]

        # Fetch all tags from a git repository.
        logr.info('Running command: {}...'.format(str(command)))
        process = subprocess.Popen(command, stdout=subprocess.PIPE)

        return process

    def parse_tags(self, tags_string=None):
        # type: (Optional[str]) -> None
        """
        Parses git api response for "git ls-remote --tags" command.

        :param tags_string: Response string.
        """
        if not tags_string:
            logr.warning('Tags string from remote git not provided. Using synchronous remote git tags fetching...')
            stdout, stderr = self.fetch_remote_tags().communicate(timeout=120)
            tags_string = stdout.decode()

        # Regex to match only those versions that contain only numbers, digits and a string 'dev-'
        regex = re.compile(r'^[dev\-0-9.]*$')

        # Split and filter out standard git api output and leave only tag strings
        output = [line.split('\t')[1].split('/')[2] for line in tags_string.splitlines()]
        # Filter our tags that do not match version structure (e.g. dev-2.0.0 or 1.5.0)
        versions = list(filter(regex.search, output))

        assert versions, 'Failed to parse versions. Versions list is empty.'

        self.remote_git_tags = versions

    def resolve_version(self):
        # type: () -> None
        """
        Sends tags off to a version resolver.

        :return:
        """
        if not self.remote_git_tags:
            logr.warning('Remote git tags not parsed. Parsing tags synchronously...')
            self.parse_tags()

        resolver = VersionResolver(self.version_to_resolve, self.remote_git_tags, self.environment)
        version = resolver.resolve_version()

        self.resolved_version = version

    def clone(self):
        # type: () -> subprocess.Popen
        """
        Clones git repository.

        :return: Process instance that is doing the project cloning part.
        """
        if not self.resolved_version:
            logr.info('No resolved version found! Resolving version synchronously...')
            self.resolve_version()

        # Create a dependency link.
        dep_link = 'git@bitbucket.org:{}.git'.format(self.git_subpath)

        # Before cloning git repo, clear directory.
        try:
            shutil.rmtree(self.src_cloned_path)
        except EnvironmentError:
            pass

        full_tag_name = ("dev-" if self.environment == 'dev' else '') + str(self.resolved_version)

        # Create clone git repository with specific version.
        command = ['git', "clone", '--depth', '1', '--branch', full_tag_name, dep_link, self.src_cloned_path]

        logr.info('Running command: {}...'.format(str(command)))
        process = subprocess.Popen(command)

        return process
