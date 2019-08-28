"""
commands.py: pinda commands
"""
import subprocess
from . import utilities
from . import data

def list():
    """
    List available packages
    """
    available = utilities.available_packages()
    installed = utilities.installed_packages()
    result = ''
    for package in available:
        if package in installed:
            line = '* '
        else:
            line = '  '
        line += '{name:10s} {version:10s} {description}\n'.format(**package)
        result += line
    return result

def install(name, version, sudo=False, user=True):
    """
    Install a package
    """
    if utilities.is_installed(name, version):
        return
    r = utilities.available_packages(name, version)
    if len(r) == 0:
        raise ValueError('Error: {} {} is not available'.format(name, version))
    r = r[0]
    pip = utilities.pip_command()
    if pip is None:
        raise RuntimeError('Error - cannot find pip or pip3 command')
    r['pip_command'] = pip
    if sudo:
        command = 'sudo {pip_command} install {repository}'.format(**r)
    else:
        if user:
            command = '{pip_command} install {repository} --user'.format(**r)
        else:
            command = '{pip_command} install {repository}'.format(**r)
    result = subprocess.check_output(command, shell=True, 
                                     universal_newlines=True, 
                                     stderr = subprocess.STDOUT)
    
def uninstall(name, version, sudo=False):
    """
    Uninstall a package
    """
    if not utilities.is_installed(name, version):
        return True
    r = utilities.available_packages(name, version)[0]
    pip = utilities.pip_command()
    if pip is None:
        raise RuntimeError('Error - cannot find pip or pip3 command')
    r['pip_command'] = pip
    if sudo:
        command = 'sudo {pip_command} uninstall -y{package}'.format(**r)
    else:
        command = '{pip_command} uninstall -y {package}'.format(**r)
    result = subprocess.check_output(command, shell=True, 
                                     universal_newlines=True, 
                                     stderr = subprocess.STDOUT)

def template():
    """
    Returns a template for a YAML file to define a new database entry.
    """
    return data.template

def update_from(yaml_file, overwrite=False):
    """
    Update the local database of available packages.

    The atgument is the name of a YAML format file that contains the 
    specification for the new database entry. A template for this can
    be generated using the "pinda template" command.
    """
    data.update_from(yaml_file, overwrite=overwrite)

def update():
    """
    Update the pinda default database.

    Downloads a fresh copy of '_default.yaml' into $HOME/.pinda.
    """
    data.update()

def info(name, version):
    """
    Returns full information about a package
    """
    r = utilities.available_packages(name, version)
    if len(r) == 0:
        raise ValueError('Error: {} {} is not available'.format(name, version))
    r = r[0]
    return r['info']
