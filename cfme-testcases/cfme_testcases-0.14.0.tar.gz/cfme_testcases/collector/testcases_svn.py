"""
Testcases data from Polarion SVN repo.
"""

import logging
import os
import re
from collections import defaultdict

from dump2polarion import svn_polarion

from cfme_testcases.exceptions import TestcasesException

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class PolarionTestcases:
    """Loads and access Polarion testcases."""

    TEST_PARAM = re.compile(r"\[.*\]")
    tc_cache = defaultdict(dict)

    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.available_testcases = {}
        wi_cache = self.tc_cache[repo_dir].get("wi_cache")
        if wi_cache:
            self.wi_cache = wi_cache
        else:
            self.wi_cache = svn_polarion.WorkItemCache(repo_dir)
            self.tc_cache[repo_dir]["wi_cache"] = self.wi_cache

    def load_active_testcases(self, lookup_by="title"):
        """Creates dict of all active testcases names and ids."""
        cached_lookup_by = self.tc_cache[self.repo_dir].get(lookup_by)
        if cached_lookup_by:
            self.available_testcases = cached_lookup_by
            return

        cases = {}
        for item in self.wi_cache.get_all_items():
            if item.get("type") != "testcase":
                continue
            case_status = item.get("status")
            if not case_status or case_status == "inactive":
                continue

            case_title = item.get(lookup_by)
            case_id = item.get("work_item_id")
            try:
                cases[case_title].append(case_id)
            except KeyError:
                cases[case_title] = [case_id]

        self.available_testcases = cases
        self.tc_cache[self.repo_dir][lookup_by] = cases

    def __getitem__(self, item):
        return self.available_testcases[item]

    def __iter__(self):
        return iter(self.available_testcases)

    def __len__(self):
        return len(self.available_testcases)

    def __contains__(self, item):
        return item in self.available_testcases

    def __repr__(self):
        return "<Testcases {}>".format(self.available_testcases)


def _load_testcases(repo_dir, lookup_by):
    polarion_testcases = PolarionTestcases(os.path.expanduser(repo_dir))
    try:
        polarion_testcases.load_active_testcases(lookup_by=lookup_by)
    except Exception as err:
        raise TestcasesException(
            "Failed to load testcases from SVN repo `{}`: {}".format(repo_dir, err)
        )
    if not polarion_testcases:
        raise TestcasesException("No testcases loaded from SVN repo `{}`.".format(repo_dir))

    return polarion_testcases


def get_missing_in_polarion(repo_dir, testcase_identifiers, lookup_by="title"):
    """Gets set of testcases missing in Polarion."""
    polarion_testcases = _load_testcases(repo_dir, lookup_by)
    return set(testcase_identifiers) - set(polarion_testcases)


def get_missing_in_source(repo_dir, testcase_identifiers, lookup_by="title"):
    """Gets set of testcases missing in source code but present in Polarion."""
    polarion_testcases = _load_testcases(repo_dir, lookup_by)
    return set(polarion_testcases) - set(testcase_identifiers)
