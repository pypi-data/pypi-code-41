from seafileapi.client import SeafileApiClient


def connect(server, username, password, token=None, verify_ssl=True):
    client = SeafileApiClient(server, username, password, token, verify_ssl)
    return client
