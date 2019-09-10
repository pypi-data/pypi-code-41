import requests
from io import BytesIO
import json


def upload_file(fname: str, server: str="http://localhost:8080/upload", params: dict=None) -> str:
    """
    Uploads the file to the DEX server and returns the token.
    Raises an exception if upload fails.

    :param fname: the name of the file to upload
    :type fname: str
    :param server: the URL of the server to upload to
    :type server: str
    :param params: the additional parameters to send to the server, eg login information (user/password)
    :type params: dict
    :return: the generated token, None if failed to upload
    :rtype: str
    :raises Exception: if the upload fails
    """

    if params is None:
        files = {}
    else:
        files = params.copy()
    files['payload'] = open(fname, 'rb')
    r = requests.post(server, files=files)
    if r.status_code == 200:
        response = json.loads(r.text)
        return response['token']
    else:
        return None


def upload_data(data: bytes, server: str="http://localhost:8080/upload", params: dict=None) -> str:
    """
    Uploads the file to the DEX server and returns the token.
    Raises an exception if upload fails.

    :param data: the data to upload
    :type data: bytes
    :param server: the URL of the server to upload to
    :type server: str
    :param params: the additional parameters to send to the server, eg login information (user/password)
    :type params: dict
    :return: the generated token, None if failed to upload
    :rtype: str
    :raises Exception: if the upload request fails
    """

    if params is None:
        files = {}
    else:
        files = params.copy()
    files['payload'] = BytesIO(data)
    r = requests.post(server, files=files)
    if r.status_code == 200:
        return r.text
    else:
        return None


def download(token: str, server: str="http://localhost:8080/download", params: dict=None) -> bytes:
    """
    Downloads the data associated with the token.

    :param token: the token to download the data for
    :type token: str
    :param server: the URL of the server to upload to
    :type server: str
    :param params: the additional parameters to send to the server, eg login information (user/password)
    :type params: dict
    :return: the downloaded data, None if failed to download
    :rtype: bytes
    """

    if params is None:
        files = {}
    else:
        files = params.copy()
    files['token'] = token
    r = requests.post(server, files=files)
    if r.status_code == 200:
        return r.content
    else:
        return None


def remove(token: str, server: str="http://localhost:8080/remove", params: dict=None) -> int:
    """
    Removes the data associated with the token.

    :param token: the token to download the data for
    :type token: str
    :param server: the URL of the server to upload to
    :type server: str
    :param params: the additional parameters to send to the server, eg login information (user/password)
    :type params: dict
    :return: the status code, None if failed to download
    :rtype: int
    """

    if params is None:
        files = {}
    else:
        files = params.copy()
    files['token'] = token
    r = requests.post(server, files=files)
    return r.status_code
