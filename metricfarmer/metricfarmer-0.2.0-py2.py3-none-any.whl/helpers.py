import copy
import os
import re

_mf_replace_re = re.compile(r':MF_REPLACE:([\w]*)$', re.VERBOSE)
_mf_env_re = re.compile(r':MF_ENV:([\w]*)$', re.VERBOSE)


def walker(param_dict, basic_dict=None):
    """
        Went through a dictionary and searches for string with a defined syntax.
        If found, the value wil be replaced by the valued taken from another parameter, which name
        was given in the string.

        Example:

        {
            "source": "Take me",
            "target": {
                "nothing": True,
                "final_target": ":MF_REPLACE:source"
            }
        }

        Fot the above case, the value of "final_target" will get replace by "take me".

        :param param_dict:
        :param basic_dict:
        :return:
        """

    mf_helpers = [
        (_mf_replace_re, mf_replace),
        (_mf_env_re, mf_env)
    ]

    if basic_dict is None:
        basic_dict = param_dict

    updated_dict = copy.deepcopy(param_dict)

    for key, value in updated_dict.items():
        if isinstance(value, dict):
            updated_dict[key] = mf_replace(value, basic_dict)
        elif isinstance(value, str):

            for helper in mf_helpers:
                m = helper[0].match(value)
                if m is not None:
                    helper_value = helper[1](m)
                    if helper_value is not None:
                        updated_dict[key] = helper_value
        else:
            pass  # If not dict or string, nothing to do

    return updated_dict


def mf_replace(m, basic_dict):
    """

    """
    try:
        param = m.groups()[0]  # There should be only one param defined
        if param in basic_dict.keys():
            return basic_dict[param]
    except Exception:
        return None


def mf_env(m, *args, **kwargs):
    """

    """
    try:
        param = m.groups()[0]  # There should be only one param defined
        env_value = os.environ.get(param, None)
        if env_value is not None:
            return env_value
        return None
    except Exception:
        return None

