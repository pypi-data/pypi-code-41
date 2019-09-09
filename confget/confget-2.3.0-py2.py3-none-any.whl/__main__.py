# Copyright (c) 2018, 2019  Peter Pentchev
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
The command-line interface to the confget module: specify some parameters
through command-line options, then display variable values or names.
"""

from __future__ import print_function

import argparse
import sys

from . import backend
from . import defs
from . import format as fmt

try:
    from typing import List, Optional

    _TYPING_USED = (defs, List, Optional)
except ImportError:
    pass


class MainConfig(fmt.FormatConfig):
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
    Extend the format config class with some output settings.

    Add the following settings:
    - check_only (boolean): only check whether a variable is defined
    - query_sections (boolean): only display the section names
    """

    def __init__(
        self,  # type: MainConfig
        check_only,  # type: bool
        filename,  # type: Optional[str]
        list_all,  # type: bool
        match_regex,  # type: bool
        match_var_names,  # type: bool
        match_var_values,  # type: Optional[str]
        name_prefix,  # type: Optional[str]
        query_sections,  # type: bool
        section,  # type: str
        section_override,  # type: bool
        section_specified,  # type: bool
        show_var_name,  # type: bool
        shell_escape,  # type: bool
        varnames,  # type: List[str]
    ):  # type: (...) -> None
        # pylint: disable=too-many-arguments,too-many-locals
        """ Store the specified configuration values. """
        super(MainConfig, self).__init__(
            filename=filename,
            list_all=list_all,
            match_regex=match_regex,
            match_var_names=match_var_names,
            match_var_values=match_var_values,
            name_prefix=name_prefix,
            section=section,
            section_specified=section_specified,
            section_override=section_override,
            show_var_name=show_var_name,
            shell_escape=shell_escape,
            varnames=varnames,
        )
        self.check_only = check_only
        self.query_sections = query_sections


def version():
    # type: () -> None
    """
    Display program version information.
    """
    print("confget " + defs.VERSION_STRING)


def features(name):
    # type: (Optional[str]) -> None
    """
    Display a list of the features supported by the program.
    """
    if name is None:
        print(
            " ".join(
                [
                    "{name}={version}".format(name=item[0], version=item[1])
                    for item in defs.FEATURES
                ]
            )
        )
    else:
        ver = dict(defs.FEATURES).get(name, None)
        if ver is None:
            sys.exit(1)
        print(ver)


def output_check_only(cfg, data):
    # type: (MainConfig, defs.ConfigData) -> None
    """ Check whether the variable is present. """
    if cfg.section not in data:
        sys.exit(1)
    elif cfg.varnames[0] not in data[cfg.section]:
        sys.exit(1)
    sys.exit(0)


def output_vars(cfg, data):
    # type: (MainConfig, defs.ConfigData) -> None
    """ Output the variable values. """
    for vitem in fmt.filter_vars(cfg, data):
        print(vitem.output_full)


def output_sections(data):
    # type: (defs.ConfigData) -> None
    """ Output the section names. """
    for name in sorted(data.keys()):
        if name != "":
            print(name)


def validate_options(args, backend_name):
    # type: (argparse.Namespace, str) -> None
    """
    Make sure the command-line options are not used in an invalid combination.
    """
    query_sections = args.query == "sections"

    if args.list_all or query_sections:
        if args.varnames:
            sys.exit("Only a single query at a time, please!")
    elif args.match_var_names:
        if not args.varnames:
            sys.exit("No patterns to match against")
    elif args.check_only and len(args.varnames) > 1:
        sys.exit("Only a single query at a time, please!")
    elif not args.varnames:
        sys.exit("No variables specified to query")

    if query_sections and backend_name != "ini":
        sys.exit(
            "The query for sections is only supported for "
            "the 'ini' backend for the present"
        )


def check_option_conflicts(args):
    # type: (argparse.Namespace) -> None
    """ Make sure that the command-line options do not conflict. """
    total = (
        int(args.query is not None)
        + int(args.match_var_names)
        + int(args.list_all)
        + int(
            bool(args.varnames)
            and not (args.match_var_names or args.query == "feature")
        )
    )
    if total > 1:
        sys.exit("Only a single query at a time, please!")


def main():
    # type: () -> None
    """
    The main program: parse arguments, do things.
    """
    parser = argparse.ArgumentParser(
        prog="confget",
        usage="""
    confget [-t ini] -f filename [-s section] varname...
    confget -V | -h | --help | --version
    confget -q features""",
    )
    parser.add_argument(
        "-c",
        action="store_true",
        dest="check_only",
        help="check whether the variables are defined in " "the file",
    )
    parser.add_argument(
        "-f",
        type=str,
        dest="filename",
        help="specify the configuration file name",
    )
    parser.add_argument(
        "-L",
        action="store_true",
        dest="match_var_names",
        help="specify which variables to display",
    )
    parser.add_argument(
        "-l",
        action="store_true",
        dest="list_all",
        help="list all variables in the specified section",
    )
    parser.add_argument(
        "-m",
        type=str,
        dest="match_var_values",
        help="only display variables with values that match "
        "the specified pattern",
    )
    parser.add_argument(
        "-N",
        action="store_true",
        dest="show_var_name",
        help="always display the variable name",
    )
    parser.add_argument(
        "-n",
        action="store_true",
        dest="hide_var_name",
        help="never display the variable name",
    )
    parser.add_argument(
        "-O",
        action="store_true",
        dest="section_override",
        help="allow variables in the specified section to "
        "override those placed before any "
        "section definitions",
    )
    parser.add_argument(
        "-p",
        type=str,
        dest="name_prefix",
        help="display this string before the variable name",
    )
    parser.add_argument(
        "-q",
        type=str,
        dest="query",
        choices=["feature", "features", "sections"],
        help="query for a specific type of information, e.g. the list of "
        "sections defined in "
        "the configuration file",
    )
    parser.add_argument(
        "-S",
        action="store_true",
        dest="shell_quote",
        help="quote the values suitably for the Bourne shell",
    )
    parser.add_argument(
        "-s",
        type=str,
        dest="section",
        help="specify the configuration file section",
    )
    parser.add_argument(
        "-t",
        type=str,
        default="ini",
        dest="backend",
        help="specify the configuration file type",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="display program version information and exit",
    )
    parser.add_argument(
        "-x",
        action="store_true",
        dest="match_regex",
        help="treat the match patterns as regular expressions",
    )
    parser.add_argument(
        "varnames", nargs="*", help="the variable names to query"
    )

    args = parser.parse_args()
    if args.version:
        version()
        return

    check_option_conflicts(args)

    if args.query == "features":
        if args.varnames:
            sys.exit("No arguments to -q features")
        features(None)
        return
    if args.query == "feature":
        if len(args.varnames) != 1:
            sys.exit("Only a single feature name expected")
        features(args.varnames[0])
        return

    query_sections = args.query == "sections"

    cfg = MainConfig(
        check_only=args.check_only,
        filename=args.filename,
        list_all=args.list_all,
        match_regex=args.match_regex,
        match_var_names=args.match_var_names,
        match_var_values=args.match_var_values,
        name_prefix=args.name_prefix,
        query_sections=query_sections,
        section=args.section if args.section is not None else "",
        section_override=args.section_override,
        section_specified=args.section is not None,
        shell_escape=args.shell_quote,
        show_var_name=args.show_var_name
        or (
            (args.match_var_names or args.list_all or len(args.varnames) > 1)
            and not args.hide_var_name
        ),
        varnames=args.varnames,
    )

    matched_backends = [
        name
        for name in sorted(backend.BACKENDS.keys())
        if name.startswith(args.backend)
    ]
    if not matched_backends:
        sys.exit(
            'Unknown backend "{name}", use "list" for a list'.format(
                name=args.backend
            )
        )
    elif len(matched_backends) > 1:
        sys.exit(
            'Ambiguous backend "{name}": {lst}'.format(
                name=args.backend, lst=" ".join(matched_backends)
            )
        )
    back = backend.BACKENDS[matched_backends[0]]

    validate_options(args, matched_backends[0])

    try:
        cfgp = back(cfg)
    except Exception as exc:  # pylint: disable=broad-except
        sys.exit(str(exc))
    data = cfgp.read_file()

    if cfg.check_only:
        output_check_only(cfg, data)
    elif query_sections:
        output_sections(data)
    else:
        output_vars(cfg, data)


if __name__ == "__main__":
    main()
