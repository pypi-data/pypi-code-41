from cfdi.utils import get_xml_object
from cfdi import CFDI
from django.test import TestCase
import os

def get_factura_str():
    tests_dir = os.path.dirname(__file__)
    with open(os.path.join(tests_dir, "data/factura.xml")) as xml_file:
        return xml_file.read()

class UtilTest(TestCase):
    def setUp(self):
        pass

    def test_load_func(self):
        from cfdi.settings import ERROR_CALLBACK
        assert callable(ERROR_CALLBACK) == True

    def test_get_xml_object(self):
        xml_factura = get_factura_str()
        xml_obj = get_xml_object(xml_factura)
        assert xml_obj.emisor.rfc == "AAA010101AAA"


class CFDITest(TestCase):

    def setUp(self):
        self.xml_factura = get_factura_str()

    def test_generar_sello(self):
        # xml_obj = get_xml_object(self.xml_factura)
        # cfdi = CFDI()
        # cfdi.generar_sello()
        pass

    def test_generar_cfdi(self):
        # cfdi = CFDI()
        # cfdi.nombre = "test"
        # cfdi.Version = "3.3"
        pass