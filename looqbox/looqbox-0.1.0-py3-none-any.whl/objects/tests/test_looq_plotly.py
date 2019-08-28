from looqbox.objects.tests import ObjPlotly
from looqbox.objects.tests import LooqObject
import unittest
import json
import plotly.plotly as py
import plotly.graph_objs as go


class TestObjectPlotly(unittest.TestCase):
    """
    Test looq_plotly file
    """

    def test_instance(self):
        data = [go.Bar(
            x=['giraffes', 'orangutans', 'monkeys'],
            y=[20, 14, 23]
        )]

        looq_object_plotly = ObjPlotly(data)

        self.assertIsInstance(looq_object_plotly, LooqObject)

    def test_json_creation(self):
        # Testing JSON keys
        data = [go.Bar(
            x=['giraffes', 'orangutans', 'monkeys'],
            y=[20, 14, 23]
        )]

        looq_object_plotly = ObjPlotly(data)
        json_keys = list(json.loads(looq_object_plotly.to_json_structure).keys())
        self.assertTrue("objectType" in json_keys, msg="objectType not found in JSON structure test")
        self.assertTrue("data" in json_keys, msg="data not found in JSON structure test")
        self.assertTrue("layout" in json_keys, msg="layout not found in JSON structure test")
        self.assertTrue("stacked" in json_keys, msg="stacked not found in JSON structure test")
        self.assertTrue("displayModeBar" in json_keys, msg="displayModeBar not found in JSON structure test")
        

if __name__ == '__main__':
    unittest.main()
