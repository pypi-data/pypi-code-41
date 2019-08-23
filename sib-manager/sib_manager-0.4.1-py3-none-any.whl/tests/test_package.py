import pytest
from sib.package import Package

def test_create_package_for_development():

    # load project from previous testing phase
    package = Package('pkg', '/tmp/sib-dev/pkg')
    assert package.create()
