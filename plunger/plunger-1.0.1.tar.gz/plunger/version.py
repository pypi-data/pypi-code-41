import pkg_resources


def get_version():
    d = pkg_resources.get_distribution(__package__.replace('_', '-'))
    return d.version


def main():
    print(get_version())
