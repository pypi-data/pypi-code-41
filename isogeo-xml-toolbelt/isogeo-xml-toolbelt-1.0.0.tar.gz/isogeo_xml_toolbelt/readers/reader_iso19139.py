# -*- coding: utf-8 -*-
#! python3

"""
    Isogeo XML Fixer - Metadata

    Purpose:     Read a metadata stored into XML ISO 19139 as an object
    Authors:     First work by GeoBretagne on mdchecker - updated by Isogeo
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
from isogeo_xml_toolbelt.models import Contact
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
class MetadataIso19139(object):
    """Object representation of a metadata stored into XML respecting ISO 19139."""

    def __init__(self, xml: Path):
        """Read and  store the input XML metadata as an object.

        :param pathlib.Path xml: path to the XML file
        """
        # lxml needs a str not a Path
        if isinstance(xml, Path):
            self.xml_path = str(xml.resolve())
        else:
            raise TypeError("XML path must be a pathlib.Path instance.")
        # ensure namespaces declaration
        self.namespaces = {
            "gts": "http://www.isotc211.org/2005/gts",
            "gml": "http://www.opengis.net/gml",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "gco": "http://www.isotc211.org/2005/gco",
            "gmd": "http://www.isotc211.org/2005/gmd",
            "gmx": "http://www.isotc211.org/2005/gmx",
            "srv": "http://www.isotc211.org/2005/srv",
            "xl": "http://www.w3.org/1999/xlink",
        }
        # parse xml
        self.md = etree.parse(self.xml_path)
        # identifiers
        self.filename = xml.name
        self.fileIdentifier = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString/text()",
            self.namespaces,
        )
        self.MD_Identifier = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/"
            "gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
            self.namespaces,
        )
        self.title = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/"
            "gmd:title/gco:CharacterString/text()",
            self.namespaces,
        )
        self.OrganisationName = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:pointOfContact/"
            "gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString/text()",
            self.namespaces,
        )
        self.abstract = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString/text()",
            self.namespaces,
        )

        # Process context and step
        self.processContext = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:dataQualityInfo/"
            "gmd:DQ_DataQuality/gmd:lineage"
            "/gmd:LI_Lineage/gmd:statement/gco:CharacterString/text()",
            self.namespaces,
        )

        self.processStep = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:dataQualityInfo/"
            "gmd:DQ_DataQuality/gmd:lineage"
            "/gmd:LI_Lineage/gmd:processStep/gmd:LI_ProcessStep/gmd:description/"
            "gco:CharacterString/text()",
            self.namespaces,
        )

        # update frequency
        self.updateFrequency = utils.xmlGetTextTag(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification"
            "/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation"
            "/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode",
            self.namespaces,
            "codeListValue",
        )

        # collection parent
        self.parentIdentifier = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:parentIdentifier/gco:CharacterString/text()",
            self.namespaces,
        )

        # vector or raster
        self.storageType = utils.xmlGetTextTag(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialRepresentationType/gmd:MD_SpatialRepresentationTypeCode",
            self.namespaces,
            "codeListValue",
        )

        # format
        self.formatName = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString/text()",
            self.namespaces,
        )
        self.formatVersion = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:version/gco:CharacterString/text()",
            self.namespaces,
        )

        # date or datetime ?
        dates_str = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/"
            "gmd:date/gmd:CI_Date/gmd:date/gco:Date/text()",
            self.namespaces,
        )
        datetimes_str = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/"
            "gmd:date/gmd:CI_Date/gmd:date/gco:DateTime/text()",
            self.namespaces,
        )
        if dates_str != "":
            self.date = utils.parse_string_for_max_date(dates_str)
        else:
            self.date = utils.parse_string_for_max_date(datetimes_str)

        # seems always datetime
        md_dates_str = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:dateStamp/" "gco:DateTime/text()",
            self.namespaces,
        )
        self.md_date = utils.parse_string_for_max_date(md_dates_str)

        # contacts
        self.list_contacts = self.get_md_contacts()

        # keywords
        self.keywords = self.get_md_keywords()

        # bounding box
        self.bbox = []
        try:
            self.lonmin = float(
                utils.xmlGetTextNodes(
                    self.md,
                    "/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/"
                    "gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/"
                    "gmd:westBoundLongitude/gco:Decimal/text()",
                    self.namespaces,
                )
            )
            self.lonmax = float(
                utils.xmlGetTextNodes(
                    self.md,
                    "/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/"
                    "gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/"
                    "gmd:eastBoundLongitude/gco:Decimal/text()",
                    self.namespaces,
                )
            )
            self.latmin = float(
                utils.xmlGetTextNodes(
                    self.md,
                    "/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/"
                    "gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/"
                    "gmd:southBoundLatitude/gco:Decimal/text()",
                    self.namespaces,
                )
            )
            self.latmax = float(
                utils.xmlGetTextNodes(
                    self.md,
                    "/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/"
                    "gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/"
                    "gmd:northBoundLatitude/gco:Decimal/text()",
                    self.namespaces,
                )
            )
        except:
            self.lonmin = -180
            self.lonmax = 180
            self.latmin = -90
            self.latmax = 90

        self.geometry = utils.xmlGetTextTag(
            self.md,
            "gmd:spatialRepresentationInfo/gmd:MD_VectorSpatialRepresentation/"
            "gmd:geometricObjects/gmd:MD_GeometricObjects/gmd:geometricObjectType/gmd:MD_GeometricObjectTypeCode",
            self.namespaces,
            "codeListValue",
        )

        # resolution for rasters

        self.resolution = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:spatialResolution/"
            "gmd:MD_Resolution/gmd:distance/gco:Distance/text()",
            self.namespaces,
        )

        # scale
        self.scale = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:identificationInfo/"
            "gmd:MD_DataIdentification/gmd:spatialResolution/"
            "gmd:MD_Resolution/gmd:equivalentScale/gmd:MD_RepresentativeFraction/"
            "gmd:denominator/gco:Integer/text()",
            self.namespaces,
        )

        # SRS
        self.srs_code = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/"
            "gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString/text()",
            self.namespaces,
        )
        self.srs_codeSpace = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/"
            "gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:codeSpace/gco:CharacterString/text()",
            self.namespaces,
        )

        # feature count
        self.featureCount = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:spatialRepresentationInfo/gmd:MD_VectorSpatialRepresentation/gmd:geometricObjects/gmd:MD_GeometricObjects/gmd:geometricObjectCount/gco:Integer/text()",
            self.namespaces,
        )

        # feature catalogs
        self.featureCatalogs = utils.xmlGetTextNodes(
            self.md,
            "/gmd:MD_Metadata/gmd:contentInfo[19]/gmd:MD_FeatureCatalogueDescription/gmd:featureCatalogueCitation/text()",
            self.namespaces,
        )

    # -- METHODS --------------------------------------------------------------
    def __repr__(self):
        return self.fileIdentifier

    def __str__(self):
        return self.fileIdentifier

    def get_md_contacts(self) -> dict:

        md_contact = list()

        root = self.md.getroot()  # get xml root

        # get contacts in gmd:contact
        for ct in root.findall("gmd:contact/", self.namespaces):

            md_contact.append(Contact(ct, self.namespaces).asDict())

        # get contacts in gmd:pointOfContact
        for pct in root.findall(
            "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/",
            self.namespaces,
        ):

            md_contact.append(Contact(pct, self.namespaces).asDict())

        return md_contact

    def get_md_keywords(self) -> list:

        md_keywords = list()

        root = self.md.getroot()  # get xml root

        # get keywords
        for kw in root.findall(
            "gmd:identificationInfo/"
            "gmd:MD_DataIdentification/"
            "gmd:descriptiveKeywords/"
            "gmd:MD_Keywords/gmd:keyword/gco:CharacterString",
            self.namespaces,
        ):

            # Test for exceptions like <gco:CharacterString>cycles ; circulations douces ; vélo ; aménagements cyclables ; transport ; véloroute ;</gco:CharacterString>
            keyword = kw.text.split(";")
            if len(keyword) > 1:
                for k in keyword:
                    md_keywords.append(k)
            else:
                md_keywords.append(kw.text)

        return md_keywords

    def asDict(self) -> dict:
        """Retrun object as a structured dictionary key: value."""
        return {
            "filename": self.filename,
            "fileIdentifier": self.fileIdentifier,
            "MD_Identifier": self.MD_Identifier,
            "type": self.storageType,
            "title": self.title,
            "abstract": self.abstract,
            "processContext": self.processContext,
            "processStep": self.processStep,
            "updateFrequency": self.updateFrequency,
            "OrganisationName": self.OrganisationName,
            "keywords": self.keywords,
            "formatName": self.formatName,
            "formatVersion": self.formatVersion,
            "contacts": self.list_contacts,
            "md_date": self.md_date,
            "date": self.date,
            "geometry": self.geometry,
            "resolution": self.resolution,
            "scale": self.scale,
            "srs": "{}:{}".format(self.srs_codeSpace, self.srs_code),
            "latmin": self.latmin,
            "latmax": self.latmax,
            "lonmin": self.lonmin,
            "lonmax": self.lonmax,
            "featureCount": self.featureCount,
            "featureCatalogs": self.featureCatalogs,
            "storageType": self.storageType,
            "parentidentifier": self.parentIdentifier,
        }


# #############################################################################
# ### Stand alone execution #######
# #################################

if __name__ == "__main__":
    """Test parameters for a stand-alone run."""
    # li_fixtures_xml = sorted(Path(r"tests/fixtures/").glob("**/*.xml"))
    # li_fixtures_xml = sorted(Path(r"input").glob("**/*.xml"))

    li_fixtures_xml = sorted(Path(r"tests\fixtures\orano_xml").glob("**/*.xml"))
    for xml_path in li_fixtures_xml:
        test = MetadataIso19139(xml=xml_path)
        print(test.asDict().get("title"), test.asDict().get("scale"))
        # print(xml_path.resolve(), test.storageType)
