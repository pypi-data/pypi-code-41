import os


def resource_path(relative_path):
    PATH = os.path.dirname(os.path.realpath(__file__))

    return PATH + relative_path
