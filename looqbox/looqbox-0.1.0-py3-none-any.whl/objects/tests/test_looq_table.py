from looqbox.objects.tests import ObjTable
from looqbox.objects.tests import LooqObject
import unittest
import json
import numpy as np
import pandas as pd


class TestObjectTable(unittest.TestCase):
    """
    Test looq_table file
    """

    def test_instance(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        self.assertIsInstance(looq_object_table, LooqObject)

    def test_json_creation(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure).keys())
        self.assertTrue("objectType" in json_table_keys, msg="objectType not found in JSON structure test")
        self.assertTrue("title" in json_table_keys, msg="title not found in JSON structure test")
        self.assertTrue("header" in json_table_keys, msg="header not found in JSON structure test")
        self.assertTrue("body" in json_table_keys, msg="body not found in JSON structure test")
        self.assertTrue("footer" in json_table_keys, msg="footer not found in JSON structure test")
        self.assertTrue("searchable" in json_table_keys, msg="searchable not found in JSON structure test")
        self.assertTrue("searchString" in json_table_keys, msg="searchString not found in JSON structure test")
        self.assertTrue("paginationSize" in json_table_keys, msg="paginationSize not found in JSON structure test")
        self.assertTrue("framed" in json_table_keys, msg="framed not found in JSON structure test")
        self.assertTrue("framedTitle" in json_table_keys, msg="framedTitle not found in JSON structure test")
        self.assertTrue("stacked" in json_table_keys, msg="stacked not found in JSON structure test")
        self.assertTrue("showBorder" in json_table_keys, msg="showBorder not found in JSON structure test")
        self.assertTrue("showOptionBar" in json_table_keys, msg="showOptionBar not found in JSON structure test")
        self.assertTrue("showHighlight" in json_table_keys, msg="showHighlight not found in JSON structure test")
        self.assertTrue("striped" in json_table_keys, msg="striped not found in JSON structure test")
        self.assertTrue("sortable" in json_table_keys, msg="sortable not found in JSON structure test")
        self.assertTrue("class" in json_table_keys, msg="class not found in JSON structure test")

    def test_header_json_structure(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON header keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure)["header"].keys())
        self.assertTrue("content" in json_table_keys, msg="content not found in header JSON structure test")
        self.assertTrue("visible" in json_table_keys, msg="visible not found in header JSON structure test")
        self.assertTrue("group" in json_table_keys, msg="group not found in header JSON structure test")

    def test_body_json_structure(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON body keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure)["body"].keys())
        self.assertTrue("content" in json_table_keys, msg="content not found in body JSON structure test")
        self.assertTrue("format" in json_table_keys, msg="format not found in body JSON structure test")
        self.assertTrue("class" in json_table_keys, msg="class not found in body JSON structure test")

    def test_footer_json_structure(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)

        # Testing JSON footer keys
        json_table_keys = list(json.loads(looq_object_table.to_json_structure)["footer"].keys())
        self.assertTrue("content" in json_table_keys, msg="content not found in footer JSON structure test")
        self.assertTrue("subtotal" in json_table_keys, msg="subtotal not found in footer JSON structure test")

    def test_subtotal_structure(self):
        data = np.array([np.arange(10)] * 2).T
        df = pd.DataFrame(data, columns=['Venda', 'Meta'])
        looq_object_table = ObjTable(df)
        looq_object_table.subtotal = {"text": "Subtotal text", "link": "Subtotal link"}
        looq_object_table2 = ObjTable(df)
        looq_object_table2.subtotal = [{"text": "Subtotal text", "link": "Subtotal link"}]
        json_table2 = json.loads(looq_object_table2.to_json_structure)


        # Testing JSON footer keys
        with self.assertRaises(Exception):
            looq_object_table.to_json_structure
        self.assertTrue(isinstance(json_table2["footer"]["subtotal"], list))


if __name__ == '__main__':
    unittest.main()
