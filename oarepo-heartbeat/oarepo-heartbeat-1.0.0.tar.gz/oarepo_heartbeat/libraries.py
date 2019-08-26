import sys

try:
    from pip._internal.utils.misc import get_installed_distributions
except ImportError:
    from pip import get_installed_distributions


def gather_libraries(*args, **kwargs):
    pkgs = get_installed_distributions()

    return (
        True, {
            'libraries': {
                x.project_name: {
                    'version': x.version,
                    'conflicts': x.check_version_conflict()
                } for x in pkgs
            }
        }
    )


def gather_python(*args, **kwargs):
    return (True, {
        'python': sys.version_info
    })


if __name__ == '__main__':
    import json

    print(json.dumps(gather_libraries(), indent=4))
