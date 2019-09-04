import semver
from typing import Union, Tuple, Callable, Any, Dict


def semver_try_parse(version):
    # type: (str) -> Tuple[bool, Union[semver.VersionInfo, None]]
    try:
        version_info = semver.parse_version_info(version)
        return True, version_info
    except ValueError:
        return False, None


def apply_for_all_dict_values(dictionary, valid, func):
    # type: (Dict, Callable[[Any], bool], Callable[[Any], Any]) -> None
    """Applies func to all values in Dictionary that match valid function.
    :param dictionary: The dictionary to iterate
    :param valid: Function that validates type or other condition for value.
    :param func: Function to apply to the value and replace it.
    """
    def _iterate(value):
        """Inner function with wider object definition then parent.
        Created to keep parent strict signature."""
        if isinstance(value, dict):
            for _, _value in value.items():
                _iterate(_value)
        elif isinstance(value, list):
            for _value in value:
                _iterate(_value)
        if valid(value):
            func(value)

    _iterate(dictionary)
