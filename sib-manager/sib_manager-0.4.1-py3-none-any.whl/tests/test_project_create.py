
import pytest
import yaml
from os import path
from sib.project import Project

def test_create_development(new_project):

    res = new_project.create(production=False, create_dir=True)
    assert res is None

def test_install_without_package(project_created):

    assert project_created.install()

def test_install_with_packages(new_packages_file):

    assert new_packages_file.install()
    assert new_packages_file.packages['djangoldp_project'] == 'djangoldp_project'
    assert new_packages_file.packages['oidc_provider'] == 'git+https://github.com/jblemee/django-oidc-provider.git@develop'

    # test installation
    try:
        import djangoldp
        import djangoldp_project
        import oidc_provider
        assert True
    except ImportError:
        assert False
