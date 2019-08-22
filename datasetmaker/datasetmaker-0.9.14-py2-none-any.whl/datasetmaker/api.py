from . import clients


def create_client(source):
    return clients.available[source]()
