import pytest
from pinda import commands, data

def test_install():
    commands.install('fpocket', '3.0')
    with pytest.raises(ValueError):
        commands.install('pocket', '3.0')
        commands.install('fpocket', '2.0')

def test_uninstall():
    commands.uninstall('fpocket', '3.0')
    commands.uninstall('pocket', '3.0')
    commands.uninstall('fpocket', '2.0')

def test_update():
    data.update_from('test/data/good_template.yaml')
    with pytest.raises(ValueError):
        data.update_from('test/data/good_template.yaml')
    data.update_from('test/data/good_template.yaml', overwrite=True)
