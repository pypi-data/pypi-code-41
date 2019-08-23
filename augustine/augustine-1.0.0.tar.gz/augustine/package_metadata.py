# coding=utf-8
from os.path import isdir
from pkg_resources import get_distribution, Distribution
from typing import Mapping

from ._core import find_package_name
from .extra_feature import ExtraFeature


class PackageMetadata(object):
    def __init__(self, package_directory=None, package=None, package_name=None):
        # type: (str, str, str) -> None
        if not package_directory and not package and not package_name:
            raise ValueError(
                'You must supply either the path to the package, the package module, or the package name.')

        if (package_name and package_directory) or (package_name and package) or (package and package_directory):
            raise ValueError(
                'You can only specify either the path to the package, the package module, or the package name, ')

        if package_directory and not isdir(package_directory):
            raise ValueError("Package directory at '{}' does not exist.".format(package_directory))

        if package and not hasattr(package, '__path__'):
            raise RuntimeError("Cannot find attribute '__path__' on package: {}".format(repr(package)))

        self._package_directory = package_directory
        self._package = package
        self._package_name = package_name
        self._extra_features = None
        self._distribution = None

    @property
    def package_name(self):
        # type: () -> str
        if self._package_name:
            return self._package_name

        package_directory = self._package_directory if self._package_directory else self._package.__path__
        self._package_name = find_package_name(package_directory)

        return self._package_name

    @property
    def distribution(self):
        # type: () -> Distribution
        if self._distribution:
            return self._distribution

        self._distribution = get_distribution(self._package_name)

        return self._distribution

    @property
    def extra_features(self):
        # type: () -> Mapping[str, ExtraFeature]
        if self._extra_features:
            return self._extra_features

        base_requirements = set(self.distribution.requires())

        extras_requirements = {
            extra: [
                self._parse_extra_requirement(requirement)
                for requirement in set(self.distribution.requires(extras=[extra])) - base_requirements]
            for extra in self.distribution.extras}

        self._extra_features = {
            name: ExtraFeature(self._package_name, name, requirements)
            for name, requirements in extras_requirements.items()}

        return self._extra_features

    @staticmethod
    def _parse_extra_requirement(requirement):
        # type: (str) -> str
        requirement = str(requirement)
        parts = requirement.split(';')
        requirement = parts[0]

        return requirement
