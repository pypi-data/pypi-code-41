# -*- coding: utf-8 -*-
#! python3

"""
    Isogeo XML Fixer - Metadata

    Purpose:     Read a metadata stored into XML ISO 19110 as an object
    Authors:     Isogeo, inspired by the work did by GeoBretagne on mdchecker
    Python:      3.6.x
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging

# 3rd party library
import arrow
from lxml import etree


# #############################################################################
# ########## Globals ###############
# ##################################

# logging
logging.basicConfig(level=logging.INFO)


# #############################################################################
# ########## Classes ###############
# ##################################


class XmlUtils(object):
    """Common methods used to parse XML files."""

    def __init__(self):
        """Instanciation."""
        super(XmlUtils, self).__init__()

    def xmlGetTextNodes(self, doc: etree._ElementTree, xpath: str, namespaces: dict):
        """Shorthand to retrieve serialized text nodes matching a specific xpath.

        :param lxml.etree._ElementTree doc: XML element to parse
        :param str xpath: Xpath to reach
        :param dict namespaces: XML namespaces like `lxml.etree.getroot().nsmap`
        """
        return ", ".join(doc.xpath(xpath, namespaces=namespaces))

    def xmlGetTextTag(
        self, doc: etree._ElementTree, xpath: str, namespaces: dict, key: str
    ):

        """Function to get information in tag when information isn't in nodes matching a specific xpath.

        :param lxml.etree._ElementTree doc: XML element to parse
        :param str xpath: Xpath to reach
        :param dict namespaces: XML namespaces like 'lxml.etree.getroot().nsmap'
        :param key : XML key to find like 'codeListValue'
        """

        tag = doc.xpath(xpath, namespaces=namespaces)
        if len(tag) > 0:
            tag = tag[0].get(key, None)
        else:
            tag = "None"

        return tag

    def parse_string_for_max_date(self, dates_as_str: str):
        """Parse string with multiple dates to extract the most recent one. Used
        to get the latest modification date.

        :param str dates_as_str: string containing dates
        """
        try:
            dates_python = []
            for date_str in dates_as_str.split(","):
                date_str = date_str.strip()
                if date_str != "":
                    date_python = arrow.get(date_str)
                    dates_python.append(date_python)
            if len(dates_python) > 0:
                return max(dates_python)
        except:
            logging.error("Date parsing error: " + dates_as_str)
            return None


# #############################################################################
# ### Stand alone execution #######
# #################################
if __name__ == "__main__":
    """Test parameters for a stand-alone run."""
    utils = XmlUtils()
