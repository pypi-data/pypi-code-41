# -*- coding: utf-8 -*-
"""
Submits collected XML files to appropriate Importers in appropriate order.
"""

from __future__ import absolute_import, unicode_literals

import logging
import threading

from cfme_testcases import utils
from cfme_testcases.exceptions import NothingToDoException, TestcasesException
from dump2polarion import properties
from dump2polarion import submit as d2p_submit
from dump2polarion import utils as d2p_utils

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class CollectedDataSubmitter(object):
    """Submitter of collected XMLs."""

    def __init__(self, submit_args, config, xmls_container, output_dir=None):
        self.submit_args = submit_args
        self.config = config
        self.xmls_container = xmls_container
        self.output_dir = output_dir

    @staticmethod
    def get_job_log(file_type, output_dir):
        """Returns filename for saving the log file."""
        if not output_dir:
            return None
        return utils.get_job_logname(file_type, output_dir)

    @staticmethod
    def _append_msg(retval, msg, succeeded, failed):
        if retval:
            succeeded.append(msg)
        else:
            failed.append(msg)

    @staticmethod
    def _log_outcome(succeeded, failed):
        if succeeded and failed:
            logger.info("SUCCEEDED to %s.", ", ".join(succeeded))
        if failed:
            raise TestcasesException("FAILED to {}.".format(", ".join(failed)))

        logger.info("DONE - RECORDS SUCCESSFULLY UPDATED!")

    def _submit_xml(self, file_type):
        xml_root = getattr(self.xmls_container, file_type)

        if xml_root is None or file_type in self.xmls_container.processed:
            raise NothingToDoException("No data to import.")
        self.xmls_container.processed.add(file_type)

        job_log = self.get_job_log(file_type, self.output_dir)
        properties.remove_response_property(xml_root)
        response = d2p_submit.submit_and_verify(
            xml_root=xml_root, config=self.config, log_file=job_log, **self.submit_args
        )
        if response:
            self.xmls_container.imported.add(file_type)
        return response

    def update_testcases_threaded(self):
        """Updates existing testcases in new thread."""
        if self.xmls_container.updated_testcases is None:
            raise NothingToDoException("No data to import.")

        job_log = self.get_job_log("updated_testcases", self.output_dir)
        properties.remove_response_property(self.xmls_container.updated_testcases)
        all_submit_args = dict(
            xml_root=self.xmls_container.updated_testcases,
            config=self.config,
            log_file=job_log,
            **self.submit_args
        )

        # run it in separate thread so we can continue without waiting
        # for the submit to finish
        def _run_submit(results, args_dict):
            retval = d2p_submit.submit_and_verify(**args_dict)
            results.append(retval)

        output = []
        updating_testcases_t = threading.Thread(target=_run_submit, args=(output, all_submit_args))
        updating_testcases_t.start()

        return updating_testcases_t, output

    def submit_file_type(self, file_type, msg, succeeded, failed):
        """Submits specified file type."""
        imported = False
        try:
            imported = self._submit_xml(file_type)
            self._append_msg(imported, msg, succeeded, failed)
        except NothingToDoException:
            pass
        return imported

    def update_testrun(self, file_type, msg, succeeded, failed):
        """Updates testrun using XML file specified by file type."""
        testrun_id = self.submit_args.get("testrun_id") or d2p_utils.get_testrun_id_config(
            self.config
        )

        xml_root = getattr(self.xmls_container, file_type)
        imported = False
        if testrun_id:
            imported = self.submit_file_type(file_type, msg, succeeded, failed)
        elif not testrun_id and xml_root is not None:
            logger.warning("Not updating testrun, testrun ID not specified.")
        return imported

    def submit_all(self):
        """Submits all outstanding XMLs to Polarion Importers.

        There should be only XMLs meant for submit in the `self.xmls_container`.
        """
        if not self.submit_args:
            return

        succeeded, failed = [], []

        # requirements are needed by testcases, update them first
        self.submit_file_type("requirements", "update requirements", succeeded, failed)

        # update existing testcases in new thread
        updating_testcases_t = None
        try:
            updating_testcases_t, output = self.update_testcases_threaded()
        except NothingToDoException:
            pass

        # import missing data
        self.submit_file_type("missing_testcases", "add missing testcases", succeeded, failed)
        if (
            "missing_testcases" in self.xmls_container.imported
            or "testcases" in self.xmls_container.imported
        ):
            self.update_testrun("missing_testsuites", "update testrun", succeeded, failed)

        # wait for update of existing testcases to finish
        if updating_testcases_t:
            updating_testcases_t.join()
            response = output.pop()
            self._append_msg(response, "update existing testcases", succeeded, failed)
            if response:
                self.xmls_container.imported.add("updated_testcases")

        # import complete data
        self.submit_file_type("testcases", "add all testcases", succeeded, failed)
        if "testcases" in self.xmls_container.imported:
            self.update_testrun("testsuites", "create testrun", succeeded, failed)

        self._log_outcome(succeeded, failed)


def submit_all(submit_args, config, xmls_container, output_dir):
    """Submits collected XML files to Polarion Importers."""
    return CollectedDataSubmitter(submit_args, config, xmls_container, output_dir).submit_all()


def _do_import(submit_args, config, xmls_container, output_dir, file_type):
    xml_root = getattr(xmls_container, file_type)

    if xml_root is None or file_type in xmls_container.processed:
        return None
    xmls_container.processed.add(file_type)

    job_log = CollectedDataSubmitter.get_job_log(file_type, output_dir)
    properties.remove_response_property(xml_root)

    response = d2p_submit.submit_and_verify(
        xml_root=xml_root, config=config, log_file=job_log, **submit_args
    )

    if not response:
        raise TestcasesException("Failed to do import.")

    xmls_container.imported.add(file_type)

    return job_log


def import_testcases(submit_args, config, xmls_container, output_dir):
    """Imports unfiltered testcases into Polarion."""
    job_log = None
    try:
        job_log = _do_import(submit_args, config, xmls_container, output_dir, "testcases")
    except TestcasesException:
        raise TestcasesException("Failed to update existing testcases.")

    logger.info("SUCCEEDED to import testcases.")
    return job_log


def initial_submit(submit_args, config, xmls_container, output_dir):
    """Submits data to Polarion to get a list of missing testcases."""
    job_log = None
    try:
        job_log = _do_import(submit_args, config, xmls_container, output_dir, "init_testsuites")
    except TestcasesException:
        raise TestcasesException("Failed to do the initial submit.")

    logger.info("SUCCEEDED to do initial import.")
    return job_log
