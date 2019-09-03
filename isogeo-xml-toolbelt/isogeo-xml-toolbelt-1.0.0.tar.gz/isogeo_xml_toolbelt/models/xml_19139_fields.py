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
import datetime
import logging
import os
from pathlib import Path
from uuid import UUID

# 3rd party library
from lxml import etree

# #############################################################################
# ########## Globals ###############
# ##################################

# logging
logging.basicConfig(level=logging.INFO)


# #############################################################################
# ########## Classes ###############
# ##################################


class Contact(object):
    """Contact in metadata XML 19139
    
    :param lxml.etree._ElementTree contact: Element {http://www.isotc211.org/2005/gmd}CI_ResponsibleParty
    :param dict namespaces: XML namespaces like `lxml.etree.getroot().nsmap`
    """

    def __init__(self, contact, namespaces):
        """Instanciation."""
        self.namespaces = namespaces
        try:
            self.name = contact.find(
                "gmd:individualName/gco:CharacterString", self.namespaces
            ).text
        except:
            self.name = None
        try:
            self.organisation = contact.find(
                "gmd:organisationName/gco:CharacterString", self.namespaces
            ).text
        except:
            self.organisation = None

        self.adr_path = "gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/"

        try:
            self.rue = contact.find(
                self.adr_path + "gmd:deliveryPoint/gco:CharacterString", self.namespaces
            ).text
        except:
            self.rue = None
        try:
            self.ville = contact.find(
                self.adr_path + "gmd:city/gco:CharacterString", self.namespaces
            ).text
        except:
            self.ville = None
        try:
            self.cp = contact.find(
                self.adr_path + "gmd:postalCode/gco:CharacterString", self.namespaces
            ).text
        except:
            self.cp = None
        try:
            self.country = contact.find(
                self.adr_path + "gmd:country/gco:CharacterString", self.namespaces
            ).text
        except:
            self.country = None
        try:
            self.mail = contact.find(
                self.adr_path + "gmd:electronicMailAddress/gco:CharacterString",
                self.namespaces,
            ).text
        except:
            self.mail = None

        try:
            self.telephone = contact.find(
                "gmd:contactInfo/gmd:CI_Contact/"
                "gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString",
                self.namespaces,
            ).text
        except:
            self.telephone = None

        try:
            self.role = contact.find("gmd:role/gmd:CI_RoleCode", self.namespaces).get(
                "codeListValue"
            )
        except:
            self.role = None

    def asDict(self) -> dict:
        """Return contact as a structured dictionary key: value."""

        return {
            "name": self.name,
            "organisation": self.organisation,
            "role": self.role,
            "rue": self.rue,
            "ville": self.ville,
            "cp": self.cp,
            "country": self.country,
            "mail": self.mail,
            "telephone": self.telephone,
        }


# #############################################################################
# ### Stand alone execution #######
# #################################
if __name__ == "__main__":
    """Test parameters for a stand-alone run."""
    namespaces = {
        "gts": "http://www.isotc211.org/2005/gts",
        "gml": "http://www.opengis.net/gml",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "gco": "http://www.isotc211.org/2005/gco",
        "gmd": "http://www.isotc211.org/2005/gmd",
        "gmx": "http://www.isotc211.org/2005/gmx",
        "srv": "http://www.isotc211.org/2005/srv",
        "xl": "http://www.w3.org/1999/xlink",
    }

    li_fixtures_xml = sorted(Path(r"input").glob("**/*.xml"))

    for xml_path in li_fixtures_xml:
        # lxml needs a str not a Path

        xml_path = str(xml_path.resolve())

        md = etree.parse(xml_path)
        root = md.getroot()  # get xml root

        # get contacts in gmd:contact
        for ct in root.findall("gmd:contact/", namespaces):

            print(Contact(ct).asDict())
