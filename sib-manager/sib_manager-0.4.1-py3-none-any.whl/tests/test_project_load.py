import pytest
from sib.project import Project

# /!\ Once django is initialized its settings are immutable /!\
# Those tests shouldn't be run from the same python instance

def test_without_package(project_created):

    assert project_created.install()
    assert project_created.load('test', 'test', 'test@test.io') is None


def test_with_packages(new_packages_file):

    assert new_packages_file.install()
    assert new_packages_file.load() is None
