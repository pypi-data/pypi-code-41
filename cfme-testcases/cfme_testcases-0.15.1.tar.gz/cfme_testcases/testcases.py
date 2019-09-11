"""
Methods for generating and working with testcases XML files.
"""

import logging

from dump2polarion import utils as d2p_utils
from dump2polarion.exporters import testcases_exporter

from cfme_testcases import utils
from cfme_testcases.exceptions import TestcasesException

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class TestcasesXML:
    """Generate XML for Testcases Importer."""

    requirements_lookup = "name"

    def __init__(self, config, tests_data_json, set_requirements=True, transform_func=None):
        self.config = config
        self.tests_data_json = tests_data_json
        self.set_requirements = set_requirements
        self.transform_func = transform_func

    def set_requirements_lookup(self, testcase_rec):
        """Sets lookup methods for requirements in testcase."""
        if testcase_rec.get("linked-items-lookup-method") in ("id", "name"):
            return
        testcase_rec["linked-items-lookup-method"] = self.requirements_lookup

    def setup_requirements(self, testcases_data):
        """Configures requirements in testcase."""
        for testcase_rec in testcases_data:
            requirement_names = testcase_rec.get("linked-items")
            if not requirement_names:
                continue
            if not self.set_requirements:
                testcase_rec.pop("linked-items", None)
                testcase_rec.pop("linked-work-items", None)
                testcase_rec.pop("linkedWorkItems", None)
                continue
            if isinstance(requirement_names, (dict, (str,))):
                requirement_names = [requirement_names]
            self.set_requirements_lookup(testcase_rec)

    def gen_testcases_xml_str(self):
        """Generates the testcases XML string."""
        try:
            testcases_data = utils.load_json_file(self.tests_data_json)["testcases"]
        except Exception as err:
            raise TestcasesException(
                "Cannot load test cases from `{}`: {}".format(self.tests_data_json, err)
            )
        self.setup_requirements(testcases_data)
        testcases = testcases_exporter.TestcaseExport(
            testcases_data, self.config, self.transform_func
        )
        return testcases.export()


def get_testcases_xml_root(config, tests_data_json, set_requirements=True, transform_func=None):
    """Returns content of testcase XML file for testcase importer."""
    testcases_xml = TestcasesXML(
        config, tests_data_json, set_requirements=set_requirements, transform_func=transform_func
    )
    testcases_str = testcases_xml.gen_testcases_xml_str()
    return d2p_utils.get_xml_root_from_str(testcases_str)


def get_all_testcases(testcases_root):
    """Gets all testcases from XML."""
    if testcases_root.tag != "testcases":
        raise TestcasesException("XML file is not in expected format.")

    testcase_instances = testcases_root.findall("testcase")
    # Expect that in ID is the value we want.
    # In case of "lookup-method: name" it's test case title.
    attr = "id"

    for testcase in testcase_instances:
        tc_id = testcase.get(attr)
        if tc_id:
            yield tc_id


def get_lookup_by(config):
    """Gets lookup-method."""
    import_props = config.get("testcase_import_properties") or {}
    lookup_by = import_props.get("lookup-method") or "id"
    if lookup_by == "name":
        lookup_by = "title"
    elif lookup_by == "custom":
        lookup_by = import_props.get("polarion-custom-lookup-method-field-id") or "testCaseID"
    elif lookup_by == "id":
        lookup_by = "work_item_id"
    return lookup_by
