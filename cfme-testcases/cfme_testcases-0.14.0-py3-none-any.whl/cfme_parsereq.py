"""
Gets CFME requirements data out of `REG_PATH` file. Used just in CFME, ignored if not present.
"""

import ast

from cfme_testcases.exceptions import TestcasesException

REQ_PATH = "cfme/test_requirements.py"


def _get_tree(filename):
    try:
        with open(filename) as infile:
            source = infile.read()

        tree = ast.parse(source, filename=filename)
    except Exception as err:
        raise TestcasesException("Cannot parse `{}`: {}".format(filename, err))

    return tree


def parse_requirements_file(tree, filename):
    """Parse the requirements info out of REQ_PATH file."""
    if not tree:
        tree = _get_tree(filename)

    requirements_data = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue

        try:
            func = node.value.func
            req_name = node.value.args[0].s
            if not (
                req_name
                and func.value.value.id == "pytest"
                and func.value.attr == "mark"
                and func.attr == "requirement"
            ):
                continue
        except AttributeError:
            continue

        requirement_record = {"title": req_name}

        try:
            keywords = node.value.keywords
        except AttributeError:
            keywords = {}

        for keyword in keywords:
            requirement_record[keyword.arg] = keyword.value.s

        requirements_data.append(requirement_record)

    return requirements_data


def get_requirements():
    """Gets the requirements info."""
    return parse_requirements_file(None, REQ_PATH)
