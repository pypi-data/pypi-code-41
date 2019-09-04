"""
Helper file that helps to install project with setup tools.
"""
import os
import shutil
import sys
import pip
import logging
import setuptools

from setuptools.command.install import install
from typing import List, Tuple, Optional
from git_dependency_python.dependency_manager import GitDependencyManager
from git_dependency_python.git_dependency import GitDependency
from git_dependency_python.pip_helper import PipHelper
from git_dependency_python.tools import create_dir

ENVIRONMENT = None  # type: str
REQUIRED_PIP_VERSION = '18.1'  # type: str
PROJECT_PREFIX = None  # type: str
PROJECT_NAME = None  # type: str
PACKAGE_VERSION = None  # type: str
DESCRIPTION = ''  # type: str
LOG_PATH = ''  # type: str
CHILD = False  # type: bool
# Arguments passed when running setup.py installation scripts.
# We expect that the list would look something like this:
# ['-c', 'install', '--record', '/tmp/pip-record-lfiadlh1/install-record.txt', '--environment=dev']
EXECUTION_ARGUMENTS = sys.argv

logr = logging.getLogger(__name__)


class InstallCommand(install):
    """
    Class for adding options to installation command.
    """
    user_options = install.user_options + [
        ('environment=', None, 'Specify a production or development environment.'),
        ('child', None, 'Specify whether this is a parent installation or a child one.'),
    ]

    def initialize_options(self):
        # type: () -> None
        install.initialize_options(self)
        self.environment = None
        self.child = None

    def finalize_options(self):
        # type: () -> None
        install.finalize_options(self)

        global ENVIRONMENT

        try:
            # Check if environment is set.
            assert ENVIRONMENT in ['dev', 'prod'], 'Bad environment set.'
        except AssertionError:
            # If not - assert that this class has a set environment.
            assert self.environment in ['dev', 'prod'], 'Bad environment propagated from parent project.'
            ENVIRONMENT = self.environment

    def run(self):
        install.run(self)


def install_deps(external_dependencies, internal_dependencies):
    # type: (List[str], List[Tuple[str, str, str]]) -> None
    """
    Installs all required dependencies for the project and the project itself.

    :param external_dependencies: External dependencies e.g. 'Django==2.0.3'.
    :param project_name: Name of your project.
    :param internal_dependencies: Internal project dependencies.

    :return: No return.
    """
    if "install" not in EXECUTION_ARGUMENTS:
        logr.info(
            'Execution arguments indicated that it is not an install action. '
            'Skipping dependencies installation... '
            'Execution arguments: {}.'.format(', '.join(EXECUTION_ARGUMENTS))
        )

        # Make sure at least setuptools setup command is called.
        setuptools_setup()

        return

    logr.info('Installing external dependencies: {}...'.format(', '.join(external_dependencies)))
    [PipHelper.install_by_pip(dependency) for dependency in external_dependencies]

    # Make sure setuptools setup command is called.
    setuptools_setup()

    # Convert a list of tuples dependencies to class objects.
    internal_dependencies = [GitDependency(*dependency, environment=ENVIRONMENT) for dependency in
                             internal_dependencies]

    logr.info('Installing internal dependencies: {}.'.format(', '.join([str(dep) for dep in internal_dependencies])))
    GitDependencyManager(internal_dependencies, CHILD, ENVIRONMENT).install()


def setuptools_setup():
    # type: () -> None
    logr.info('Running setup command by setuptools... Execution arguments: {}.'.format(str(EXECUTION_ARGUMENTS)))

    setuptools.setup(
        name=PROJECT_NAME,
        version=PACKAGE_VERSION,
        packages=setuptools.find_packages(),
        description=DESCRIPTION,
        cmdclass={'install': InstallCommand},
        include_package_data=True,
    )


def setup_logging(clean=True):
    # type: (bool) -> None
    global LOG_PATH

    # Set logging path.
    LOG_PATH = "/tmp/{}/{}/install/debug/dump.txt".format(PROJECT_PREFIX, PROJECT_NAME)

    if clean:
        try:
            shutil.rmtree(os.path.dirname(LOG_PATH))
            create_dir(LOG_PATH)
        except FileNotFoundError:
            create_dir(LOG_PATH)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ])

    logr.info('Successfully initialized logging module!')


def prepare_setup(package_version, project_name, description, project_prefix):
    # type: (str, str, str, str) -> None
    """
    Ensures that setup() by setup tools can be called without errors and all parts are set.

    :param package_version: The version of the current project that is being installed.
    :param project_name: The name of the current project that is being installed.

    :return: No return.
    """
    global PACKAGE_VERSION
    PACKAGE_VERSION = package_version

    global PROJECT_NAME
    PROJECT_NAME = project_name

    global DESCRIPTION
    DESCRIPTION = description

    global PROJECT_PREFIX
    PROJECT_PREFIX = project_prefix

    pip_version = pip.__version__

    assert pip_version == REQUIRED_PIP_VERSION, 'Unsupported pip version ({}), must be {}.'.format(pip_version, REQUIRED_PIP_VERSION)

    if "install" not in EXECUTION_ARGUMENTS:
        logr.info('Skipping other preparation steps because it is not an installation action.')
        return

    # Prepare logging library.
    setup_logging()

    # Ensure a right environment is provided.
    parse_environment()

    parse_child()

    logr.info(
        'Installing in {} environment.\n'
        'Project name: {}.\n'
        'Installable project version: {}.\n'
        'Execution arguments: {}.\n'.format(ENVIRONMENT, PROJECT_NAME, PACKAGE_VERSION, EXECUTION_ARGUMENTS)
    )


def parse_child():
    # type: () -> None
    global CHILD

    for arg in EXECUTION_ARGUMENTS:
        # We expect to find a key in execution arguments that start with '--child'
        if arg.startswith('--child'):
            # We expect to find a child flag formatted like this: --child.
            CHILD = True
            # Remove the argument to avoid breaking for other projects.
            sys.argv.remove(arg)
            break


def parse_environment():
    # type: () -> None
    def check_env(env):
        environment = None
        global ENVIRONMENT

        for arg in EXECUTION_ARGUMENTS:
            # We expect to find a key in execution arguments that start with '--environment'
            if arg.startswith('--environment'):
                # We expect to find an environment flag formatted like this: --environment=dev.
                # We take the second argument after splitting to get the environment string.
                environment = arg.split('=')[1]
                # Remove the argument to avoid breaking for other projects.
                sys.argv.remove(arg)
                break

        if environment:
            # We found environment in --environment flag.
            assert environment in ['dev', 'prod'], 'Invalid environment ({}) in --environment flag.'.format(environment)
            ENVIRONMENT = environment
            return

        if env in EXECUTION_ARGUMENTS:
            # We found environment in execution arguments list.
            sys.argv.remove(env)
            ENVIRONMENT = env
            return

    # Save the environment package in globals.
    check_env('dev')
    check_env('prod')

    assert ENVIRONMENT in ['dev', 'prod'], 'Invalid environment supplied! Expected \'dev\' or \'prod\'.'
