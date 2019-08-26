import re

from survey_monkey.helpers.Constants import DEFAULT_ADDRESS, PARAMETER_REGEX


def read_file(file_location):
    """
    Reads the file stored at :param file_location

    :param file_location: absolute path for the file to be read (string)
    :return: contents of file (string)
    """

    try:
        with open(file_location, "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


def get_param_names(path):
    """
    Returns list of parameter names from the path.
    For example, given the endpoint "groups/{group_id}", this function will return ["group_id"]

    :param path: Survey Monkey API endpoint path (string)
    :return: (list)
    """

    return re.findall(PARAMETER_REGEX, path)


def get_full_endpoint_path(path, param_names, args):
    """
    Get the full path for the api endpoint, includes parameters

    :param path: Survey Monkey API endpoint path. For example, "survey/{survey_id}" (string)
    :param param_names: Parameter names ["survey_id"] (list)
    :param args: List of arguments that will be assigned to the parameters (list)
    :return: (string)
    """

    params = {
        param_name: args[i]
        for i, param_name in enumerate(param_names)
    }
    return path.format(**params)


def get_headers(headers, access_token):
    """
    Updates the headers with the Survey Monkey API access token

    :param headers: HTTP headers (from request) (dict)
    :param access_token: Survey Monkey access token (string)
    :return: (dict)
    """

    updated_headers = dict(headers)
    updated_headers.update({
        "Authorization": "Bearer {0}".format(access_token),
        "Content-Type": "application/json"
    })
    return updated_headers


def get_url(version, path, address=DEFAULT_ADDRESS):
    """
    Returns full url for the API request

    :param version: API version. For example, "v3" (at the time of writing) (string)
    :param path: API endpoint path with arguments. For example, "survey/177282517" (string)
    :param address: API address. For example "http://api.surveymonkey.net" (string)
    :return: (string)
    """

    return address + "/" + version + "/" + path
