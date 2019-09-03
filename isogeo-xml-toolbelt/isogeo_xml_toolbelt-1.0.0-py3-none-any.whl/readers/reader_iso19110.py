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

# submodules
from isogeo_xml_toolbelt.utils import XmlUtils

# #############################################################################
# ########## Globals ###############
# ##################################

# logging
logging.basicConfig(level=logging.INFO)

# utils
utils = XmlUtils()

# #############################################################################
# ########## Classes ###############
# ##################################
class MetadataIso19110(object):
    """Object representation of a metadata stored into XML respecting ISO 19110."""

    def __init__(self, xml: Path):
        """Read and  store the input XML metadata as an object.

        :param pathlib.Path xml: path to the XML file
        """
        # lxml needs a str not a Path
        if isinstance(xml, Path):
            self.xml_path = str(xml.resolve())
        else:
            raise TypeError("XML path must be a pathlib.Path instance.")
        # set nampespaces
        self.namespaces = {
            "gco": "http://www.isotc211.org/2005/gco",
            "geonet": "http://www.fao.org/geonetwork",
            "gfc": "http://www.isotc211.org/2005/gfc",
            "gmd": "http://www.isotc211.org/2005/gmd",
            "gml": "http://www.opengis.net/gml",
            "gmx": "http://www.isotc211.org/2005/gmx",
            "gts": "http://www.isotc211.org/2005/gts",
            "srv": "http://www.isotc211.org/2005/srv",
            "xlink": "http://www.w3.org/1999/xlink",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }
        # parse xml
        self.md = etree.parse(self.xml_path)
        # identifiers
        self.filename = xml.name
        try:
            self.fileIdentifier = UUID(xml.name)
        except ValueError:
            pass
        # name <--> equivalent to title
        self.name = utils.xmlGetTextNodes(
            self.md,
            "/gfc:FC_FeatureCatalogue/gfc:name/gco:CharacterString/text()",
            self.namespaces,
        )
        # field of application
        self.fieldOfapplication = utils.xmlGetTextNodes(
            self.md,
            "/gfc:FC_FeatureCatalogue/gfc:fieldOfApplication/gco:CharacterString/text()",
            self.namespaces,
        )

        # organization
        self.OrganisationName = utils.xmlGetTextNodes(
            self.md,
            "/gfc:FC_FeatureCatalogue/gfc:producer/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString/text()",
            self.namespaces,
        )

        # version date or datetime
        dates_str = utils.xmlGetTextNodes(
            self.md,
            "/gfc:FC_FeatureCatalogue/gfc:versionDate/gco:Date/text()",
            self.namespaces,
        )
        datetimes_str = utils.xmlGetTextNodes(
            self.md,
            "/gfc:FC_FeatureCatalogue/gfc:versionDate/gco:DateTime/text()",
            self.namespaces,
        )
        if dates_str != "":
            self.date = utils.parse_string_for_max_date(dates_str)
        else:
            self.date = utils.parse_string_for_max_date(datetimes_str)

        # contacts
        self.contact = {
            "email": self.md.xpath(
                "/gfc:FC_FeatureCatalogue/gfc:producer/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString/text()",
                namespaces=self.namespaces,
            ),
            "address": self.md.xpath(
                "/gfc:FC_FeatureCatalogue/gfc:producer/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString/text()",
                namespaces=self.namespaces,
            ),
            "postalCode": self.md.xpath(
                "/gfc:FC_FeatureCatalogue/gfc:producer/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:postalCode/gco:CharacterString/text()",
                namespaces=self.namespaces,
            ),
            "city": self.md.xpath(
                "/gfc:FC_FeatureCatalogue/gfc:producer/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city/gco:CharacterString/text()",
                namespaces=self.namespaces,
            ),
        }

        # feature types
        featTypeName = utils.xmlGetTextNodes(
            self.md,
            "/gfc:FC_FeatureCatalogue/gfc:featureType/gfc:FC_FeatureType/gfc:typeName/gco:LocalName/text()",
            self.namespaces,
        )
        featTypeUuid = utils.xmlGetTextNodes(
            self.md,
            "/gfc:FC_FeatureCatalogue/gfc:featureType/gfc:FC_FeatureType/@uuid",
            self.namespaces,
        )
        self.featureTypes = {"name": featTypeName, "uuid": featTypeUuid}

        # attributes
        self.featureAttributes = {}

        for item in self.md.xpath(
            "/gfc:FC_FeatureCatalogue/gfc:featureType/gfc:FC_FeatureType/gfc:carrierOfCharacteristics",
            namespaces=self.namespaces,
        ):
            attrName = item.xpath(
                "gfc:FC_FeatureAttribute/gfc:memberName/gco:LocalName/text()",
                namespaces=self.namespaces,
            )[0]
            attrDescr = item.xpath(
                "gfc:FC_FeatureAttribute/gfc:definition/gco:CharacterString/text()",
                namespaces=self.namespaces,
            )[0]
            attrtype = item.xpath(
                "gfc:FC_FeatureAttribute/gfc:valueType/gco:TypeName/gco:aName/gco:CharacterString/text()",
                namespaces=self.namespaces,
            )[0]

            self.featureAttributes.setdefault(attrName, []).append(
                [attrDescr, attrtype]
            )
        # print(self.featureAttributes)

    def __repr__(self):
        return self.fileIdentifier

    def __str__(self):
        return self.fileIdentifier

    def asDict(self):
        """Return the metadata object as a dict."""
        return {
            "filename": self.filename,
            # "fileIdentifier": self.fileIdentifier,
            "name": self.name,
            "title": self.name,
            "fieldOfApplication": self.fieldOfapplication,
            "date": self.date,
            "OrganisationName": self.OrganisationName,
            "contact": self.contact,
            "featureTypes": self.featureTypes,
            "featureAttributes": self.featureAttributes,
        }


# #############################################################################
# ### Stand alone execution #######
# #################################

if __name__ == "__main__":
    """Test parameters for a stand-alone run."""
    li_fixtures_xml = sorted(Path(r"tests/fixtures").glob("**/*.xml"))
    li_fixtures_xml += sorted(Path(r"input/CD92/Catalogue d'attribut").glob("**/*.xml"))
    for xml_path in li_fixtures_xml:
        test = MetadataIso19110(xml=xml_path)
        print(
            "Filename: " + test.filename,
            "MD name: " + test.name,
            "Org: " + test.OrganisationName,
            # "Features types: " + test.featureTypes.,
            test.featureAttributes,
        )
