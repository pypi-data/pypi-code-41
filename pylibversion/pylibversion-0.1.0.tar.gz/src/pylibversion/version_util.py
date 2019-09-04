import os

import requests

DEFAULT_PYPI_HOST = "pypi.org"


def version_tuple_to_str(version_tuple):
    """
    Convert the given version tuple to a string.

    :param version_tuple: Version tuple to convert.
    :return: String representation of version tuple.
    """
    return ".".join([str(x) for x in version_tuple])


def lookup_latest_version_in_pypi(project_name, pypi_hostname=DEFAULT_PYPI_HOST):
    """
    Lookup the latest version of the given project published to pypi.

    :param project_name: Name of project in pypi.
    :param pypi_hostname: Hostname of pypi server to query.
    :return: Latest version of project published to pypi.
    """
    endpoint = "https://{host}/pypi/{project}/json".format(
        host=pypi_hostname, project=project_name
    )
    response = requests.get(endpoint)
    response.raise_for_status()

    return response.json()["info"]["version"]


def _find_version_line_in_file(file_path):
    """
    Find and return the line in the given file containing `VERSION`.

    :param file_path: Path to file to search.
    :return: Line in file containing `VERSION`.
    """
    with open(str(file_path), "r") as fileh:
        version_lines = [
            line for line in fileh.readlines() if line.startswith("VERSION")
        ]
        if len(version_lines) != 1:
            raise ValueError(
                "Unable to determine 'VERSION' in {file}".format(file=file_path)
            )
        return version_lines[0]


def lookup_local_module_version(path_to_module_name):
    """
    Lookup VERSION defined for local module.

    This function assumes that the version will be defined as a tuple in the `__init__.py` file
    at the root of the module under the `VERSION` variable.

    For example,
    ```
    VERSION = (1, 0, 0)
    ```

    :param path_to_module_name: path to module to lookup.
    :return: Version tuple for specified module.
    """
    path_to_init = os.path.join(str(path_to_module_name), "__init__.py")
    version_tuple = eval(_find_version_line_in_file(path_to_init).split("=")[-1])
    return version_tuple_to_str(version_tuple)
