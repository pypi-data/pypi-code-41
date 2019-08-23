
import pytest
import yaml
from os import path
from sib.project import Project

@pytest.fixture
def new_project(tmp_path):
    return Project('sibproject', path.join(tmp_path,'tests'))

@pytest.fixture
def project_created(new_project):

    """Created a project tree with default parameters"""

    new_project.create(production=False, create_dir=True)
    return new_project

@pytest.fixture
def new_packages_file(project_created):

    """Add packages in configuration"""

    # write a package section in config
    packages = {
        'ldppackages': {
            'djangoldp_project': 'djangoldp_project',
            'oidc_provider': 'git+https://github.com/jblemee/django-oidc-provider.git@develop'
        }
    }

    with open(project_created.deps_file, 'w') as f:
        yaml.dump(packages, f, default_flow_style=False)

    return project_created
