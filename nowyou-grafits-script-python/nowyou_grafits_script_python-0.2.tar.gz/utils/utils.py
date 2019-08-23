import os


def resource_path(relative_path):
    PATH = os.path.dirname(os.path.dirname(__file__))

    return os.path.join(PATH, relative_path)