# -*- coding: utf-8 -*-
"""
Collects all the XML files needed for import.
"""

from __future__ import absolute_import, unicode_literals

import copy
import logging

from cfme_testcases import submit, utils
from cfme_testcases.collector import filters, missing
from cfme_testcases.exceptions import NothingToDoException, TestcasesException
from dump2polarion import properties

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class XMLsCollector(object):
    """Methods for collecting XML files for import."""

    # pylint: disable=too-many-arguments
    def __init__(self, args, submit_args, config, testsuites_root, testcases_root):
        self.args = args
        self.submit_args = submit_args
        self.config = config
        self.testsuites_root = testsuites_root
        self.testcases_root = testcases_root

    def _initial_submit(self, xmls_container):
        """Submits XML to Polarion and saves the log file returned by the message bus."""
        if self.args.use_svn and not self.args.testrun_init:
            # no need to submit, SVN is used to generate list of missing testcases
            return None

        if not self.submit_args:
            raise NothingToDoException(
                "Instructed not to submit and as the import log is missing, "
                "there's nothing more to do."
            )

        if self.testsuites_root is None:
            raise TestcasesException("Cannot init testrun, testsuites XML not generated.")

        xml_root = copy.deepcopy(self.testsuites_root)

        if self.args.testrun_init:
            # want to init new test run
            dry_run = self.submit_args.get("dry_run") or False
            if self.args.testrun_title:
                properties.xunit_fill_testrun_title(xml_root, self.args.testrun_title)
        else:
            # want to just get the log file without changing anything
            dry_run = True
            # don't want to use template with dry-run
            properties.remove_property(xml_root, "polarion-testrun-template-id")

        init_sargs = self.submit_args.copy()
        init_sargs["dry_run"] = dry_run

        xmls_container.init_testsuites = xml_root
        return submit.initial_submit(init_sargs, self.config, xmls_container, self.args.output_dir)

    def get_multiple(self):
        """Gets filtered XMLs separated into multiple files."""
        xmls_container = utils.XMLsContainer()
        xmls_container.testcases = self.testcases_root
        xmls_container.testsuites = self.testsuites_root if self.args.testrun_id else None

        init_logname = self._initial_submit(xmls_container)
        missing_testcases = missing.get_missing_in_polarion(
            self.config, self.testcases_root, init_logname, self.args.use_svn
        )

        filters.add_filtered_xmls(
            xmls_container, missing_testcases, data_in_code=self.args.data_in_code
        )

        if self.args.no_testcases_update:
            xmls_container.updated_testcases = None

        # we don't want to submit unfiltered files
        xmls_container.testcases = None
        xmls_container.testsuites = None

        return xmls_container

    def get_single(self):
        """Gets single XML for each importer."""
        xmls_container = utils.XMLsContainer()
        xmls_container.testcases = self.testcases_root

        if self.args.mark_missing:
            # add data for testcases missing in source code
            marked_xml_root = missing.mark_missing_in_source(
                self.config, self.testcases_root, self.args.use_svn
            )
            xmls_container.testcases = marked_xml_root

        if not self.args.testrun_id:
            logger.warning("Not updating testrun, testrun ID not specified.")
            return xmls_container

        if self.args.testrun_init:
            if self.args.testrun_title:
                properties.xunit_fill_testrun_title(self.testsuites_root, self.args.testrun_title)
            xmls_container.testsuites = self.testsuites_root
            return xmls_container

        testcases_logname = None
        if self.submit_args:
            # Not initializing new testrun, we need to add just new testcases to existing testrun.
            # We'll submit testcases and parse produced log file to figure out what testcases
            # are missing in the testrun.
            testcases_logname = submit.import_testcases(
                self.submit_args, self.config, xmls_container, self.args.output_dir
            )

        if not (testcases_logname or self.args.use_svn):
            raise NothingToDoException("The import log is missing, there's nothing more to do.")

        missing_testcases = missing.get_missing_in_polarion(
            self.config, self.testcases_root, testcases_logname, self.args.use_svn
        )

        missing_testsuites_xml_root = filters.XMLFilters(
            None, self.testsuites_root, missing_testcases
        ).get_missing_testsuites()

        xmls_container.missing_testsuites = missing_testsuites_xml_root

        return xmls_container


def get_xmls(args, submit_args, config, testsuites_root, testcases_root):
    """Returns XMLsContainer object with all relevant XML files."""
    xmls_collector = XMLsCollector(args, submit_args, config, testsuites_root, testcases_root)
    if args.no_testcases_update or not args.data_in_code:
        return xmls_collector.get_multiple()
    return xmls_collector.get_single()
