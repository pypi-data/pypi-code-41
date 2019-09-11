"""
Find testcases that are missing in Polarion or source code.
"""

import copy
import logging
import os

from dump2polarion import parselogs
from lxml import etree

from cfme_testcases import testcases, utils
from cfme_testcases.collector import testcases_svn
from cfme_testcases.exceptions import TestcasesException

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class MissingInPolarion:
    """Testcases missing in Polarion."""

    def __init__(self, config, all_testcases, init_logname, svn_dir):
        self.config = config
        self.all_testcases = all_testcases
        self.init_logname = init_logname or ""
        self.svn_dir = svn_dir

    def get_missing_from_log(self):
        """Gets missing testcases from log file."""
        lookup_method = self.config.get("xunit_import_properties") or {}
        lookup_method = lookup_method.get("polarion-lookup-method") or "id"
        parsed_log = parselogs.parse(self.init_logname)

        if lookup_method == "name":
            missing = [item.name for item in parsed_log.new_items]
        elif lookup_method == "custom":
            missing = [item.custom_id for item in parsed_log.new_items]
        elif lookup_method == "id":
            missing = [item.id for item in parsed_log.new_items]

        return set(missing)

    def get_missing_from_svn(self):
        """Gets missing testcases using SVN repo."""
        lookup_by = testcases.get_lookup_by(self.config)
        return testcases_svn.get_missing_in_polarion(
            self.svn_dir, self.all_testcases, lookup_by=lookup_by
        )

    def get_missing(self):
        """Returns list of missing testcases."""
        utils.check_lookup_methods(self.config)
        log_exists = os.path.isfile(self.init_logname)
        if self.svn_dir and not log_exists:
            missing = self.get_missing_from_svn()
        elif not log_exists:
            raise TestcasesException(
                "The submit log file `{}` doesn't exist.".format(self.init_logname)
            )
        else:
            missing = self.get_missing_from_log()
        return missing


def get_missing_in_polarion(config, testcases_root, init_logname, svn_dir):
    """Returns list of missing testcases in Polarion."""
    all_testcases = testcases.get_all_testcases(testcases_root)
    return MissingInPolarion(config, all_testcases, init_logname, svn_dir).get_missing()


def _get_missing_in_source(config, testcases_root, svn_dir):
    """Gets set of testcases missing in source code."""
    all_testcases = testcases.get_all_testcases(testcases_root)
    lookup_by = testcases.get_lookup_by(config)
    return testcases_svn.get_missing_in_source(svn_dir, all_testcases, lookup_by=lookup_by)


def _append_missing_testcases(parent_element, missing_ids):
    """Appends testcases data to XML for testcases missing in source code."""
    for missing_id in missing_ids:
        testcase = etree.SubElement(parent_element, "testcase", {"id": missing_id})
        custom_fields_el = etree.SubElement(testcase, "custom-fields")
        etree.SubElement(
            custom_fields_el, "custom-field", {"id": "tags", "content": "NOT_FOUND_IN_SOURCES"}
        )


def mark_missing_in_source(config, testcases_root, svn_dir):
    """Mark testcases missing in source code."""
    if not svn_dir:
        logger.warning("Not marking testcases missing in source code, SVN repo not specified.")
        return testcases_root

    utils.check_lookup_methods(config)
    xml_root = copy.deepcopy(testcases_root)
    missing_ids = _get_missing_in_source(config, xml_root, svn_dir)
    _append_missing_testcases(xml_root, missing_ids)
    return xml_root
