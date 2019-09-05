# encoding: utf-8

import unittest

from fdutil.tree_search import TreeSearch


def uppercase_fields(obj,
                     fields,
                     **_):
    for field in fields:
        try:
            obj[field] = obj[field].upper()
        except KeyError:
            pass


class TestTreeSearch(unittest.TestCase):

    TEST_DICT = {"id": "1234567",
                 "list": [{"f1": "Value 1",
                           "list": [{"f1": "item 1", "f2": "value 1 item 1"},
                                    {"f1": "item 2", "f2": "value 1 item 2"},
                                    {"f1": "item 3", "f2": "value 1 item 3"},
                                    {"f1": "item 4", "f2": "value 1 item 4"},
                                    {"f1": "item 5", "f2": "value 1 item 5"},
                                   ],
                           },
                          {"f1": "Value 2",
                           "list": [{"f1": "item 1", "f2": "value 2 item 1"},
                                    {"f1": "item 2", "f2": "value 2 item 2"},
                                    {"f1": "item 3", "f2": "value 2 item 3"},
                                    {"f1": "item 4", "f2": "value 2 item 4"},
                                    ],
                           },
                          {"f1": "Value 3",
                           "list": [{"f1": "item 1", "f2": "value 3 item 1"},
                                    {"f1": "item 2", "f2": "value 3 item 2"},
                                    {"f1": "item 3", "f2": "value 3 item 3"},
                                    ],
                           },
                          ],
                 }

    def setUp(self):
        self.ts = TreeSearch(default_key='f1',
                             zero_index=False)
        self.ts_zero_index = TreeSearch(default_key='f1')

    def tearDown(self):
        pass

    # is_dictionary
    def test_1_level_deep(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list"])

        assert len(matched_nodes) == 3

    def test_2_levels_deep(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list", "Value 1"])

        assert len(matched_nodes) == 1
        assert matched_nodes[0].get("f1") == "Value 1"

    def test_3_levels_deep(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list", "Value 1", "list"])

        assert len(matched_nodes) == 5
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 1 item 1"
        assert matched_nodes[-1]["f2"] == "value 1 item 5"

    def test_3_levels_deep_with_index(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list", 2, "list"], )

        assert len(matched_nodes) == 4
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 2 item 1"
        assert matched_nodes[-1]["f2"] == "value 2 item 4"

    def test_0_index_3_levels_deep_with_index(self):
        matched_nodes = self.ts_zero_index.search(tree=self.TEST_DICT,
                                                  path=["list", 1, "list"], )

        assert len(matched_nodes) == 4
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 2 item 1"
        assert matched_nodes[-1]["f2"] == "value 2 item 4"

    def test_3_levels_deep_with_implicit_full_list(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list", "list"])

        assert len(matched_nodes) == 12
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 1 item 1"
        assert matched_nodes[-1]["f2"] == "value 3 item 3"

    def test_3_levels_deep_with_implicit_full_list_and_index(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list", "list", 2])

        assert len(matched_nodes) == 3
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 1 item 2"
        assert matched_nodes[1]["f2"] == "value 2 item 2"
        assert matched_nodes[2]["f2"] == "value 3 item 2"

    def test_0_index_3_levels_deep_with_implicit_full_list_and_index(self):
        matched_nodes = self.ts_zero_index.search(tree=self.TEST_DICT,
                                                  path=["list", "list", 1])

        assert len(matched_nodes) == 3
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 1 item 2"
        assert matched_nodes[1]["f2"] == "value 2 item 2"
        assert matched_nodes[2]["f2"] == "value 3 item 2"

    def test_3_levels_deep_with_implicit_full_list_and_default_key_match(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list", "list", "item 3"])

        assert len(matched_nodes) == 3
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 1 item 3"
        assert matched_nodes[1]["f2"] == "value 2 item 3"
        assert matched_nodes[2]["f2"] == "value 3 item 3"

    def test_3_levels_deep_with_implicit_full_list_and_explicit_key_match(self):
        matched_nodes = self.ts.search(tree=self.TEST_DICT,
                                       path=["list", "list", {"f2": "value 1 item 4"}])

        assert len(matched_nodes) == 1
        assert isinstance(matched_nodes[0], dict)
        assert matched_nodes[0]["f2"] == "value 1 item 4"
        assert matched_nodes[0]["f1"] == "item 4"

    def test_apply_uppercase_fields(self):
        assert self.TEST_DICT["list"][0]["list"][3]["f1"] == "item 4"
        assert self.TEST_DICT["list"][0]["list"][3]["f2"] == "value 1 item 4"

        self.ts.search(tree=self.TEST_DICT,
                       path=["list", "list", {"f2": "value 1 item 4"}],
                       func=uppercase_fields,
                       fields=["f2", "f1"])

        assert self.TEST_DICT["list"][0]["list"][3]["f1"] == "ITEM 4"
        assert self.TEST_DICT["list"][0]["list"][3]["f2"] == "VALUE 1 ITEM 4"

    def test_run_func_against_objects(self):

        matched_objects = self.ts.search(tree=self.TEST_DICT,
                                         path=["list", "list", {"f2": "value 3 item 2"}])

        assert self.TEST_DICT["list"][2]["list"][1]["f1"] == "item 2"
        assert self.TEST_DICT["list"][2]["list"][1]["f2"] == "value 3 item 2"

        self.ts.run_func_against_objects(func=uppercase_fields,
                                         objects=matched_objects,
                                         fields=["f2", "f1"])

        assert self.TEST_DICT["list"][2]["list"][1]["f1"] == "ITEM 2"
        assert self.TEST_DICT["list"][2]["list"][1]["f2"] == "VALUE 3 ITEM 2"

