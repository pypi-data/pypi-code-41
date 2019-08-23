import subprocess
import sys
import time
import logging

from typing import List
from git_dependency_python.dependency_lock_manager import DependencyLockManager
from git_dependency_python.git_dependency import GitDependency

logr = logging.getLogger(__name__)


class GitDependencyManager:
    """
    Manages downloading and installation of git dependencies.
    """
    def __init__(self, git_dependencies, is_child, environment='dev'):
        # type: (List[GitDependency], bool, str) -> None
        """
        Constructor function.

        :param git_dependencies: list of all git dependencies.
        :param is_child: Determines whether this is the root installation or a child.
        :param environment: Specified either production or development environment.
        """
        self.git_dependencies = {dep.project_name: dep for dep in git_dependencies}
        self.environment = environment
        self.is_child = is_child
        assert self.environment in ['dev', 'prod'], 'Bad environment.'

    def install(self):
        # type: () -> None
        """
        Clones and installs all git dependencies with optimizations.

        :return: No return.
        """
        start = time.time()
        self.__fetch_and_resolve_tags()
        finish = time.time()
        tags_delta = finish - start

        start = time.time()
        self.__download_all_dependencies()
        finish = time.time()
        clone_delta = finish - start

        start = time.time()
        self.__install_all_from_git()
        finish = time.time()
        install_delta = finish - start

        logr.info('Fetched and resolved tags in {} seconds.'.format(tags_delta))
        logr.info('Downloaded all git dependencies in {} seconds.'.format(clone_delta))
        logr.info('Installed all git dependencies in {} seconds.'.format(install_delta))

    def __fetch_and_resolve_tags(self):
        # type: () -> None
        """
        Fetches all version tags for internal dependencies and resolves them into a single matching one.

        :return:
        """
        processes = {}

        # Create processes to fetch tags in parallel.
        for dependency_name, dependency in self.git_dependencies.items():
            assert dependency_name == dependency.project_name, 'Key name and project name differ. Something is wrong.'

            # Create process to fetch tags.
            process = dependency.fetch_remote_tags()
            processes[dependency.project_name] = process

        # Fetch all tags.
        for dependency_name, process in processes.items():
            # Wait for process to finish.
            stdout, stderr = process.communicate(120)
            self.git_dependencies[dependency_name].parse_tags(stdout.decode())

        # Resolve tags.
        for dependency in self.git_dependencies.values():
            dependency.resolve_version()

    def __download_all_dependencies(self):
        # type: () -> None
        """
        Download all internal dependencies from git repositories in parallel.

        :return: No return.
        """
        processes = []

        for dependency in self.git_dependencies.values():
            process = dependency.clone()
            processes.append(process)

        for process in processes:
            # Wait for process to finish.
            process.wait()

    def __install_all_from_git(self):
        # type: () -> None
        """
        Installs a downloaded internal dependency package synchronously.

        :return: No return.
        """
        # Run installation script for that dependency.
        command = ['./install.sh', sys.executable, self.environment, '--child']
        if not self.is_child:
            file = DependencyLockManager(create=True)
            del file

        for dep in self.git_dependencies.values():
            file = DependencyLockManager()
            installed = file.read()
            try:
                version = installed.get(dep.project_name)
                if version is None:
                    logr.info('Running command: {}.'.format(str(command)))
                    installed[dep.project_name] = dep.resolved_version

                    file.update(installed)
                    del file

                    subprocess.check_call(command, cwd=dep.src_cloned_path)
                elif dep.resolved_version == version:
                    logr.info("Skipping dependency {} because it is already installed.".format(dep.src_cloned_path))
                else:
                    message = 'Failed to install dependency {} due to version clash. ' \
                              'Installed version is {} and currently trying to install {}.'

                    logr.error(message.format(
                        dep.src_cloned_path,
                        installed.get(dep.project_name),
                        dep.resolved_version
                    ))

                    raise Exception
            except subprocess.CalledProcessError as ex:
                logr.error('Failed to install dependency {}.'.format(dep.src_cloned_path), ex)
                raise

        if not self.is_child:
            file = DependencyLockManager()
            file.remove()
