# Copyright (c) 2018, 2019  Peter Pentchev <roam@ringlet.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
Filter and format a subset of the configuration variables.
"""

import fnmatch
import re

try:
    from typing import Callable, Dict, Iterable, NamedTuple, List, Optional

    _TYPING_USED = (Callable, Dict, Iterable, List, Optional)

    FormatOutput = NamedTuple(
        "FormatOutput",
        [
            ("name", str),
            ("value", str),
            ("output_name", str),
            ("output_value", str),
            ("output_full", str),
        ],
    )
except ImportError:
    import collections

    FormatOutput = collections.namedtuple(  # type: ignore
        "FormatOutput",
        ["name", "value", "output_name", "output_value", "output_full"],
    )

from . import defs


class FormatConfig(defs.Config):
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
    Extend the config class with some output settings.

    Add the following settings:
    - list_all (boolean): list all variables, not just a subset
    - match_regex (boolean): for match_var_names and match_var_values,
      perform regular expression matches instead of filename pattern ones
    - match_var_names (boolean): treat the variable names specified as
      patterns and display all variables that match those
    - match_var_values (string): display only the variables with values
      that match this pattern
    - name_prefix (string): when displaying variable names, prefix them
      with this string
    - show_var_name (boolean): display the variable names, not just
      the values
    - shell_escape (boolean): format the values in a manner suitable for
      the Bourne shell
    """

    def __init__(
        self,  # type: FormatConfig
        varnames,  # type: List[str]
        filename=None,  # type: Optional[str]
        list_all=False,  # type: bool
        match_regex=False,  # type: bool
        match_var_names=False,  # type: bool
        match_var_values=None,  # type: Optional[str]
        name_prefix=None,  # type: Optional[str]
        section="",  # type: str
        section_override=False,  # type: bool
        section_specified=False,  # type: bool
        show_var_name=False,  # type: bool
        shell_escape=False,  # type: bool
    ):  # type: (...) -> None
        # pylint: disable=too-many-arguments
        """ Store the specified configuration values. """
        super(FormatConfig, self).__init__(
            filename=filename,
            section=section,
            section_specified=section_specified,
            varnames=varnames,
        )
        self.list_all = list_all
        self.match_regex = match_regex
        self.match_var_names = match_var_names
        self.match_var_values = match_var_values
        self.name_prefix = name_prefix
        self.section_override = section_override
        self.shell_escape = shell_escape
        self.show_var_name = show_var_name

    def __repr__(self):
        # type: (FormatConfig) -> str
        return "{tname}({varnames}, {attrs})".format(
            tname=type(self).__name__,
            varnames=repr(self.varnames),
            attrs=", ".join(
                [
                    "{name}={value}".format(
                        name=name, value=repr(getattr(self, name))
                    )
                    for name in [
                        "filename",
                        "list_all",
                        "match_regex",
                        "match_var_names",
                        "match_var_values",
                        "name_prefix",
                        "section",
                        "section_override",
                        "section_specified",
                        "show_var_name",
                        "shell_escape",
                    ]
                ]
            ),
        )


def get_check_function(cfg, patterns):
    # type: (FormatConfig, List[str]) -> Callable[[str], bool]
    """
    Get a function that determines whether a variable name should be
    included in the displayed subset.
    """
    if cfg.match_regex:
        re_vars = [re.compile(name) for name in patterns]

        def check_re_vars(key):
            # type: (str) -> bool
            """ Check that the key matches any of the specified regexes. """
            return any(rex.search(key) for rex in re_vars)

        return check_re_vars

    def check_fn_vars(key):
        # type: (str) -> bool
        """ Check that the key matches any of the specified patterns. """
        return any(fnmatch.fnmatch(key, pattern) for pattern in patterns)

    return check_fn_vars


def get_varnames(cfg, sect_data):
    # type: (FormatConfig, Dict[str, str]) -> Iterable[str]
    """ Get the variable names that match the configuration requirements. """
    if cfg.list_all:
        varnames = sect_data.keys()  # type: Iterable[str]
    elif cfg.match_var_names:
        check_var = get_check_function(cfg, cfg.varnames)
        varnames = [name for name in sect_data.keys() if check_var(name)]
    else:
        varnames = [name for name in cfg.varnames if name in sect_data]

    if not cfg.match_var_values:
        return varnames

    check_value = get_check_function(cfg, [cfg.match_var_values])
    return [name for name in varnames if check_value(sect_data[name])]


def filter_vars(cfg, data):
    # type: (FormatConfig, defs.ConfigData) -> Iterable[FormatOutput]
    """
    Filter the variables in the configuration file according to
    the various criteria specified in the configuration.
    Return an iterable of FormatOutput structures allowing the caller to
    process the variable names and values in various ways.
    """
    if cfg.section_override:
        sect_data = data[""]
    else:
        sect_data = {}
    if cfg.section in data:
        sect_data.update(data[cfg.section])

    varnames = get_varnames(cfg, sect_data)
    res = []  # type: List[FormatOutput]
    for name in sorted(varnames):
        if cfg.name_prefix:
            output_name = cfg.name_prefix + name
        else:
            output_name = name

        value = sect_data[name]
        if cfg.shell_escape:
            output_value = "'{esc}'".format(
                esc="'\"'\"'".join(value.split("'"))
            )
        else:
            output_value = value

        if cfg.show_var_name:
            output_full = "{name}={value}".format(
                name=output_name, value=output_value
            )
        else:
            output_full = output_value

        res.append(
            FormatOutput(
                name=name,
                value=value,
                output_name=output_name,
                output_value=output_value,
                output_full=output_full,
            )
        )

    return res
