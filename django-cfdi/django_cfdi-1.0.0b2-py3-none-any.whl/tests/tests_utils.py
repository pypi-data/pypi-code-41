from cfdi.utils import get_xml_object
from django.test import TestCase
import os

class UtilTest(TestCase):
    def setUp(self):
        pass

    def test_get_xml_object(self):
        tests_dir = os.path.dirname(__file__)
        with open(os.path.join(tests_dir, "data/factura.xml")) as xml_file:
            xml_obj = get_xml_object(xml_file.read())
            assert xml_obj.emisor.rfc == "AAA010101AAA"