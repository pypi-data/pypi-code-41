# coding=utf-8
from typing import Any, Callable, Generic, Sequence, TypeVar

from ._core import log


ProtectedType = TypeVar('ProtectedType')


class FeatureNotInstalledException(Exception):
    def __init__(self, feature, error_message=None):
        # type: (ExtraFeature, str) -> None
        self._feature = feature

        if not error_message:
            error_message = ''
        else:
            error_message = '. '

        message = "{}Feature '{}' was not installed with package '{}'".format(
            error_message, feature.name, feature.package_name)

        super(Exception, self).__init__(message)

    @property
    def feature(self):
        # type: () -> ExtraFeature
        return self._feature


class ExtraFeature(object):
    def __init__(self, package_name, name, requirements):
        # type: (str, str, Sequence[str]) -> None
        self._package_name = package_name
        self._name = name
        self._requirements = requirements

    @property
    def package_name(self):
        return self._package_name

    @property
    def name(self):
        # type: () -> str
        return self._name

    def is_installed(self):
        # type: () -> bool
        for module in self._requirements:
            try:
                __import__(module)
            except ImportError:
                log.debug("Unable to import module {} while determining if feature '{}' is installed".format(
                    module, self._name))
                return False

        return True

    def protect(self, loader, error_message=None):
        # type: (Callable[ProtectedType], str) -> _ProtectedObject

        return _ProtectedObject(self, loader, error_message)

    def raise_not_installed(self, error_message=None):
        raise FeatureNotInstalledException(self, error_message)


class _ProtectedObject(Generic[ProtectedType], object):
    def __init__(self, feature, loader, error_message=None):
        # type: (ExtraFeature, Callable[ProtectedType], str) -> None
        self._feature = feature
        self._loader = loader
        self._error_message = error_message
        self._protected_object = None

    def __call__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        if self._protected_object:
            return self._protected_object

        if not self._feature.is_installed():
            self._feature.raise_not_installed(self._error_message)

        self._protected_object = self._loader()

        return self._protected_object(*args, **kwargs)
