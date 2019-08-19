# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SDK utilities dealing with the runtime environment."""
from typing import cast, Optional
import json
import logging
from pkg_resources import RequirementParseError, Requirement  # type: ignore
import re

from automl.client.core.common.exceptions import ClientException
from azureml.automl.core import package_utilities
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.core import RunConfiguration


class _Package:
    """A class to identify packages."""

    def __init__(self, name, regex, is_conda, required_version=None):
        """
        Create a package representation.

        :param name: The name of the pacakge.
        :type name: str
        :param regex: The regex to search for in conda depedencies.
        :type regex: str
        :param is_conda: The flag to determine if package should be a conda package.
        :type is_conda: bool
        :param required_version: The version specifier. Should follow PEP 440.
        :type required_version: str
        """
        self.name = name
        self.regex = regex
        self.is_conda = is_conda

        if required_version is not None:
            try:
                specifier = Requirement.parse(name + required_version).specifier  # type: ignore
                if len(specifier) < 1:
                    # ensure version specifier is complete. If length is 0 then only a number was provided
                    raise ClientException("Invalid version specifier. Ensure version follows PEP 440 standards.")
            except RequirementParseError:
                raise ClientException("Invalid version specifier. Ensure version follows PEP 440 standards.")
        self.required_version = required_version


def modify_run_configuration(settings: AutoMLBaseSettings,
                             run_config: RunConfiguration,
                             logger: logging.Logger) -> RunConfiguration:
    """Modify the run configuration with the correct version of AutoML and pip feed."""
    from azureml.core.conda_dependencies import CondaDependencies, DEFAULT_SDK_ORIGIN

    installed_packages = package_utilities._all_dependencies()

    defaults_pkg = "azureml-defaults"
    explain_pkg = "azureml-explain-model"

    automl_pkg = "azureml-train-automl"
    automl_regex = r"azureml\S*automl\S*"

    # For now we will add dataprep to ensure we pin to the locally installed version
    # incase the release does not match the azureml-core release cadence
    dataprep_pkg = "azureml-dataprep"
    dataprep_regex = r"azureml\S*dataprep\S*"

    numpy_pkg = "numpy"
    numpy_regex = r"numpy([\=\<\>\~0-9\.\s]+|\Z)"

    automl_version = installed_packages[automl_pkg]     # type: Optional[str]
    if automl_version and ("dev" in automl_version or automl_version == "0.1.0.0"):
        automl_version = None
        logger.warning("You are running a developer or editable installation of required packages. Your "
                       "changes will not be run on your remote compute. Latest versions of "
                       "azureml-core and azureml-train-automl will be used unless you have "
                       "specified an alternative index or version to use.")
    azureml_ver_str = "==" + automl_version if automl_version else ""

    required_package_list = [
        _Package(automl_pkg, automl_regex, False),
        _Package(dataprep_pkg, dataprep_regex, False),
        _Package(numpy_pkg, numpy_regex, True),
    ]

    dependencies = run_config.environment.python.conda_dependencies
    # if debug flag sets an sdk_url use it
    if settings.sdk_url is not None:
        dependencies.set_pip_option("--index-url " + settings.sdk_url)
        dependencies.set_pip_option("--extra-index-url " + DEFAULT_SDK_ORIGIN)

    # if debug_flag sets packages, use those in remote run
    if settings.sdk_packages is not None:
        for package in settings.sdk_packages:
            dependencies.add_pip_package(package)

    all_pkgs_str = " ".join(dependencies.pip_packages) + " " + " ".join(dependencies.conda_packages)

    # include required packages
    for p in required_package_list:
        if not re.findall(p.regex, all_pkgs_str):
            logger.info("Package {} missing from dependencies file.".format(p.name))
            # when picking version - check if we require a specific version first
            # if not, then use what is installed. If the package doesn't require a version
            # and doesnt have an installed version don't pin.
            if p.required_version is not None:
                version_str = p.required_version
                logger.info("Using pinned version: {}{}".format(p.name, version_str))
            elif p.name in installed_packages:
                ver = installed_packages[p.name]
                version_str = "=={}".format(ver)
                logger.info("Using installed version: {}{}".format(p.name, version_str))
            else:
                version_str = ""

            if p.is_conda:
                dependencies.add_conda_package(p.name + version_str)
            else:
                dependencies.add_pip_package(p.name + version_str)

            # If azureml-train-automl is added by the SDK, we need to ensure we do not pin to an editable installtion.
            # If automl_version is none we will reset the version to not pin. We also need to ensure azureml-* packages
            # are the same version as automl so we will always pin them when we pin azureml-train-automl. We only
            # assert this behavior if the user has not added automl to their conda dependencies.
            if p.name == automl_pkg:
                if automl_version is None:
                    dependencies.add_pip_package(p.name)
                    dependencies.add_pip_package(defaults_pkg)
                    dependencies.add_pip_package(explain_pkg)
                else:
                    logger.info("Pinning {} version: {}{}".format(defaults_pkg, defaults_pkg, azureml_ver_str))
                    dependencies.add_pip_package(defaults_pkg + azureml_ver_str)
                    logger.info("Pinning {} version: {}{}".format(explain_pkg, explain_pkg, azureml_ver_str))
                    dependencies.add_pip_package(explain_pkg + azureml_ver_str)

    # If we installed from a channel that isn't pypi we'll need to pick up the index. We'll assume
    # if the user added an index to their dependencies they know what they are doing and we won't modify anything.
    source_url = CondaDependencies.sdk_origin_url()
    if source_url != DEFAULT_SDK_ORIGIN and 'index-url' not in dependencies.serialize_to_string():
        dependencies.set_pip_option("--index-url " + source_url)
        dependencies.set_pip_option("--extra-index-url " + DEFAULT_SDK_ORIGIN)

    run_config.environment.python.conda_dependencies = dependencies
    return run_config


def log_user_sdk_dependencies(run, logger):
    """
    Log the AzureML packages currently installed on the local machine to the given run.

    :param run: The run to log user depenencies.
    :param logger: The logger to write user dependencies.
    :return:
    :type: None
    """
    dependencies = {'dependencies_versions': json.dumps(package_utilities.get_sdk_dependencies())}
    logger.info("[RunId:{}]SDK dependencies versions:{}."
                .format(run.id, dependencies['dependencies_versions']))
    run.add_properties(dependencies)
