from argparse import ArgumentParser
import os
import subprocess
import sys
import tempfile
import re
import warnings

from . import __version__


# specify the version of the pre-commit library to be used in pip install --upgrade
_pre_commit_version = 'pre-commit==1.*'
_dsbuild_version = '0.0.7'
_azure_yaml_file = 'azure.yml'

_python_version_regex = r'[ ]+python_version:.+([0-9]+)[.]([0-9]+)[.]([0-9]+)'
_dsvenv_version_regex = r'[ ]+dsvenv_version:.+([0-9]+)[.]([0-9]+)[.]([0-9]+)'

_VENV_BIN_DIRS = {'win32': 'Scripts',
                  'linux': 'bin',
                  'darwin': 'bin'}

_VENV_PRECOMMIT_EXECUTABLES = {'win32': 'pre-commit.exe',
                               'linux': 'pre-commit',
                               'darwin': 'pre-commit'}


def get_versions_from_azure_yaml():
    """
    Parse the version of python and dsvenv that is defined in the azure.yml file.
    If no azure.yml file exists, the returned versions will be None.

    Returns:
        tuple(str or None, str or None):
            The version of python and the version of dsvenv.
    """
    azure_yaml_path = os.path.join(os.getcwd(), _azure_yaml_file)
    if not os.path.exists(azure_yaml_path):
        return None, None

    with open(azure_yaml_path) as fid:
        azure_yaml = fid.read()
    try:
        r = re.findall(_python_version_regex, azure_yaml)
        azure_python_version = '.'.join(r[0])
    except IndexError:
        azure_python_version = None
    try:
        r = re.findall(_dsvenv_version_regex, azure_yaml)
        azure_dsvenv_version = '.'.join(r[0])
    except IndexError:
        azure_dsvenv_version = None

    return azure_python_version, azure_dsvenv_version


def verify_environment(only_warning=True):
    """
    Verify if the environment that is being used is

    Args:
        only_warning (bool): throw only a warning or a full error.
    """
    expected_python, expected_dsvenv = get_versions_from_azure_yaml()

    print('  Verifying environment...')

    this_python = '.'.join([str(sys.version_info.major),
                           str(sys.version_info.minor),
                           str(sys.version_info.micro)])
    this_dsvenv = __version__

    if expected_python is not None and expected_python != this_python:
        msg = (f'The current python version ({this_python}) is not the same as the '
               f'version that was used during testing ({expected_python}).')
        if only_warning:
            warnings.warn(msg)
        else:
            raise EnvironmentError(msg)

    if expected_dsvenv is not None and expected_dsvenv != this_dsvenv:
        msg = (f'The current dsvenv version ({this_dsvenv}) is not the same as '
               f'the version that was used during testing ({expected_dsvenv}).')
        if only_warning:
            warnings.warn(msg)
        else:
            raise EnvironmentError(msg)


def get_venv_executable(venv_dir, executable, required=True):
    """
    Return the full path to an executable inside a given virtual environment.

    Args:
        venv_dir (str): Path to the directory containing the virtual environment.
        executable (str): Name of the executable.
        required (bool): Whether to consider it a fatal error if the executable is not found.

    Returns:
        str or None: Full path to an executable inside the virtual environment. In case it cannot be found,
                     either an exception is raised or None is returned, depending on whether the executable is
                     required or not.

    Raises:
        EnvironmentError: When the current platform is not compatible with dsvenv.
        FileNotFoundError: When the executable is required and could not be found.
    """
    if sys.platform not in _VENV_BIN_DIRS:
        raise EnvironmentError(f'Unsupported platform {sys.platform} detected.')

    venv_executable_path = os.path.join(venv_dir, _VENV_BIN_DIRS[sys.platform], executable)
    venv_executable = venv_executable_path if os.path.exists(venv_executable_path) else None

    if required and not venv_executable:
        raise FileNotFoundError(f'The virtual environment executable could not be '
                                f'found: {venv_executable_path}')

    return venv_executable


def get_venv_python(venv_dir, required=True):
    """
    Return the Python executable inside a given virtual environment.

    Args:
        venv_dir (str): Path to the directory containing the virtual environment.
        required (bool): Whether to consider it a fatal error if the executable is not found.

    Returns:
        str or None: Full path to the Python executable inside the virtual environment. In case it cannot be
                     found, either an exception is raised or None is returned, depending on whether the
                     executable is required or not.

    Raises:
        FileNotFoundError: When the executable is required and could not be found.
    """
    return get_venv_executable(venv_dir=venv_dir, executable=os.path.basename(sys.executable),
            required=required)


def clear_venv(venv_dir):
    """
    Clear a virtual environment present in a given directory and restore it to a clean state. Note that this
    does not mean simply removing the entire folder, but rather uninstalls everything, leaving behind only
    those packages that are available in a fresh virtual environment (i.e., `pip` and `setuptools`).

    Args:
        venv_dir (str): Path to the directory containing the virtual environment.
    """
    vpython = get_venv_python(venv_dir, required=False)

    if not vpython:
        # Nothing to do.
        return

    # First get the list of all packages that should be uninstalled.
    reqs_file = tempfile.NamedTemporaryFile(delete=False, prefix='requirements.txt_')
    with reqs_file as fout:
        subprocess.check_call([vpython, '-m', 'pip', 'freeze'], stdout=fout)

    # Then actually remove them.
    subprocess.check_call([vpython, '-m', 'pip', 'uninstall', '-r', reqs_file.name, '-y'])

    # Clean up.
    os.remove(reqs_file.name)


def ensure_venv(venv_dir, python_version='system'):
    """
    Ensure the presence of a virtual environment in a given directory. If it already exists, nothing will be
    done. If it does not exist, the environment will be created and it will be ensured that the available
    `pip` and `setuptools` packages are updated to the latest version.
    """
    assert python_version == 'system', 'Currently only `system` Python version is supported.'

    if get_venv_python(venv_dir, required=False) is None:
        # Initialize the virtual environment.
        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])

    vpython = get_venv_python(venv_dir)

    # Ensure recent versions of pip and setuptools.
    subprocess.check_call([vpython, '-m', 'pip', 'install', '--upgrade', 'pip',
                           'setuptools'])

    # Ensure correct version of dsbuild.
    subprocess.check_call([vpython, '-m', 'pip', 'install',
                           f'dsbuild=={_dsbuild_version}'])

    # verify the environment
    verify_environment()


def initialize_venv(venv_dir, reqs_file, extra_reqs=None, install_pre_commit=True):
    """
    Initialize a virtual environment with default Python version, based on a given
    requirements file.

    Args:
        venv_dir (str): Path to a virtual environment.

        reqs_file (str): Path to the requirements file to be installed.

        extra_reqs (None or list of str): Paths to extra requirements files
        to be installed.

        install_pre_commit (bool): Whether to install the pre-commit library in the
            virtual environment.

    Raises:
        ValueError: If `reqs_file` does not exist.
    """
    if not os.path.exists(reqs_file):
        raise ValueError(f'Provided requirements file `{reqs_file}` does not exist.')

    ensure_venv(venv_dir)

    # upgrade pre-commit to the latest 1.* version
    if install_pre_commit:
        subprocess.check_call([get_venv_python(venv_dir), '-m', 'pip', 'install',
                               '--upgrade', _pre_commit_version])

    # install the requirements file and extra reqs files
    cmd_args = [get_venv_python(venv_dir), '-m', 'pip', 'install', '-r', reqs_file]

    if extra_reqs is None:
        extra_reqs = []
    for extra_reqs_file in extra_reqs:
        cmd_args += ['-r', extra_reqs_file]

    subprocess.check_call(cmd_args)


def get_default_reqs_file():
    reqs_file = os.path.join(os.getcwd(), 'requirements.txt')
    if not os.path.exists(reqs_file):
        reqs_file = None
    return reqs_file


def main():
    parser = ArgumentParser(
            description='Create and initialize a virtual environment based on a '
                        'requirements file. If a `.pre-commit-config.yaml` is present, '
                        'pre-commit hooks will be installed.')
    parser.add_argument('venv_dir', nargs='?', default=os.path.join(os.getcwd(), '.venv'),
            help='Directory containing the virtual environment.')
    parser.add_argument('--requirement', '-r', default=get_default_reqs_file(),
            help='Optional path to the requirements file to be used.')
    parser.add_argument('--clear', '-c', default=False, action='store_true',
            help='If given, clear an already existing virtual environment before initializing it with '
                 'the provided requirements.')
    parser.add_argument('--force-remove', default=False, action='store_true',
            help='If given, fully remove an already existing virtual environment before initializing it '
                 'with the provided requirements.')
    parser.add_argument('--no-pre-commit', default=False, action='store_true',
                        help='If given, pre-commit hooks will not be installed.')
    parser.add_argument('--extra-reqs', '-er', action='append',
                        help='Optional path to the requirements file to be used.')
    args = parser.parse_args()

    pre_commit_config = os.path.join(os.getcwd(), '.pre-commit-config.yaml')
    setup_pre_commit = (not args.no_pre_commit and
                        os.path.exists(pre_commit_config))

    if args.force_remove:
        # Let's open the discussion if somebody would like to actually fully remove the venv dir:
        assert False, '## Not implemented yet. Is it really needed?'
    elif args.clear:
        print(f"## Clearing venv at '{args.venv_dir}'...")
        clear_venv(venv_dir=args.venv_dir)

    if args.requirement:
        print(f"## Initializing venv at '{args.venv_dir}'\n"
              f"   using requirements file '{args.requirement}'...\n")
        initialize_venv(venv_dir=args.venv_dir, reqs_file=args.requirement,
                        extra_reqs=args.extra_reqs,
                        install_pre_commit=setup_pre_commit)
    else:
        print(f'## Ensuring venv at \'{args.venv_dir}\'...')
        ensure_venv(venv_dir=args.venv_dir)

    print('## Virtual environment successfully initialized!\n')

    if setup_pre_commit:
        print('## Installing pre-commit hooks...')
        pre_commit_exec = get_venv_executable(venv_dir=args.venv_dir,
                                              executable=_VENV_PRECOMMIT_EXECUTABLES[sys.platform],
                                              required=True)
        subprocess.check_call([pre_commit_exec, 'install'])
        print('## Pre-commit hooks successfully installed!')


if __name__ == '__main__':
    main()
