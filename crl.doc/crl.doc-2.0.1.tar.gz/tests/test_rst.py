# pylint: disable=W0212
import os
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ElementTree
import pytest

from mock import MagicMock
from crl.doc.rsttablecreator import RstTableCreator  # pylint: disable=E0401


__copyright__ = 'Copyright (C), 2019 Nokia'


@pytest.fixture
def param_list():
    return [['1', '12', '123'], ['45', '567']]


@pytest.fixture
def rst_table_creator():
    return RstTableCreator()


def test_prepare_list(rst_table_creator, param_list):
    expected = (['1', '12', '123'], ['45', '567', ' '])
    assert rst_table_creator._prepare_list(param_list) == expected


def test_column_elem_max_lengths(rst_table_creator, param_list):
    expected = (2, 3, 3)
    assert rst_table_creator._column_elem_max_lengths(param_list) == expected


def test_make_border(rst_table_creator):
    lst = (1, 2, 3, 4, 5)
    expected = "\n=  ==  ===  ====  =====\n"
    assert rst_table_creator._make_border(lst) == expected


def test_tabulate(rst_table_creator, param_list):
    expected = "\n\n\n==  ===  ===\n" \
               "1   12   123\n" \
               "45  567     \n\n" \
               "==  ===  ===\n\n"
    assert rst_table_creator._tabulate(param_list) == expected


def test_make_row(rst_table_creator):
    line = "| hello| world|"
    expected = ['hello', 'world']
    assert rst_table_creator._make_row(line) == expected


def test_change_table_to_rst_table(rst_table_creator):
    expected = "\n\n\n" \
               "=======\n" \
               "ute-doc\n\n" \
               "=======\n\n\n" \
               "test\n"
    rsttable = rst_table_creator._change_table_to_rst_table("| ute-doc |\ntest")
    assert rsttable == expected


def test_change_robot_table_to_rst_table(rst_table_creator):
    root = etree.Element("doc")
    tree = ElementTree(root)
    root.text = "| ute-doc |"
    tree.write(open("test.xml", "wb"))
    rst_table_creator._tabulate = MagicMock(side_effect="ute-doc")
    rst_table_creator.change_robot_table_to_rst_table("test.xml")
    rst_table_creator._tabulate.assert_called_with([['ute-doc']])
    os.remove("test.xml")
