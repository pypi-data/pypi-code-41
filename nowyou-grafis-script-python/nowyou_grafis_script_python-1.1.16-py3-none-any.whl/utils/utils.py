import os


def get_path():
    print(os.path.dirname(os.path.realpath(__file__)))
    print(os.path.dirname(os.path.dirname(__file__)))

def resource_path(relative_path):
    PATH = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(PATH, relative_path)