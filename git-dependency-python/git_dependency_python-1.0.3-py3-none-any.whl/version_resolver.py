import logging

from typing import List, Tuple

logr = logging.getLogger(__name__)


class VersionResolver:
    """
    Class for resolving unresolved package versions.
    """
    def __init__(self, version_to_resolve, versions_list, environment='dev'):
        # type: (str, List[str], str) -> None
        """
        Constructor.

        :param version_to_resolve: Version string that needs to be resolved e.g. 2.*.*.
        :param versions_list: A list of versions.
        :param environment: Environment - dev or prod.
        """
        self.environment = environment
        assert self.environment in ['dev', 'prod'], 'Bad environment supplied.'

        self.versions_list = versions_list
        assert self.versions_list, 'Versions list not provided.'

        self.version_to_resolve = version_to_resolve
        assert self.version_to_resolve, 'Version to resolve not provided.'

    def resolve_version(self):
        # type: () -> str
        """
        Resolves a git tagged version. E.g. If version to resolve is 2.*.*, function fetches all
        tags from a provided git repository and assigns latest tags to wildcards in version to resolve string.

        :return: Resolved version string.
        """
        # Split version to resolve string into major, minor and patch versions
        major, minor, patch = self.version_to_resolve.split('.')

        # Separate development versions
        dev_versions = [version.replace('dev-', '') for version in self.versions_list if version.__contains__('dev')]
        # Separate production versions
        prod_versions = [version for version in self.versions_list if not version.__contains__('dev')]

        # Set versions list to work with depending on environment (dev or prod)
        versions = dev_versions if self.environment == 'dev' else prod_versions  # type: List[str]

        # Split version strings  into a list of 3 integers: major, minor and patch versions
        versions = [[int(version) for version in version_string.split('.')] for version_string in versions]
        # Sort in reverse versions so the latest version would be at index 0
        versions.sort(key=lambda version: (version[0], version[1], version[2]), reverse=True)

        # Create a function that resolves each subversion independently
        def resolve_subversion(versions, index, subversion):
            # type: (List[str], int, str) -> Tuple[List[str], str]
            """
            Resolves a subversion of version, either major, minor or patch

            :param versions: List of all available versions.
            :param index: Determines whether to resolve major, minor or patch subversion.
            :param subversion: Unresolved versions subversion.

            :return: A cleaned list that satisfy subversion and a resolved subversion itself.
            """
            if subversion != '*':
                versions = [vrs for vrs in versions if vrs[index] == int(subversion)]

            return versions, versions[0][index]

        try:
            # Resolve major version first
            versions, resolved_major = resolve_subversion(versions, 0, major)
            # Resolve minor version second
            versions, resolved_minor = resolve_subversion(versions, 1, minor)
            # Resolve patch version last
            versions, resolved_patch = resolve_subversion(versions, 2, patch)
        except IndexError:
            logr.error('Failed to resolve version for: {}'.format(self.version_to_resolve))
            raise ValueError('Failed to resolve {}.'.format(self.version_to_resolve))

        # Return a resolved version string which corresponds to input version to resolve
        resolved_version = str(resolved_major) + '.' + str(resolved_minor) + '.' + str(resolved_patch)

        # Make sure version was resolved
        assert resolved_version, 'Bad version supplied. Version: {}'.format(self.version_to_resolve)
        logr.info("Resolved version for {}: {}".format(self.version_to_resolve, resolved_version))

        return resolved_version
