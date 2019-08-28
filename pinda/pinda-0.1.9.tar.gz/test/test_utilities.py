import pytest
from pinda import utilities, commands

def test_docker_available():
    result = utilities.docker_installed()
    assert result is True

def test_available_all():
    result = utilities.available_packages()
    assert type(result) == list

def test_available_specific():
    result = utilities.available_packages('gromacs')
    assert len(result) == 2
    for r in result:
        assert r['name'] == 'gromacs'

def test_available_specific_version():
    result = utilities.available_packages('gromacs', '2019')
    assert len(result) == 1
    for r in result:
        assert r['version'] == '2019'
    
def test_installed_packages():
    commands.install('gromacs', '2019')
    result = utilities.installed_packages('gromacs', '2019')
    assert len(result) == 1
    result = utilities.is_installed('gromacs', '2019')
    assert result == True
    result = utilities.is_installed('gromacs', '2019-cuda')
    assert result == False
