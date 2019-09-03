# -*- coding: UTF-8 -*-
#! python3

from __future__ import absolute_import, print_function, unicode_literals

# -----------------------------------------------------------------------------
# Name:         Metadata XML fixer
# Purpose:      Add missing elements to XML ISO19139 files
# Python:       3.5+
# Author:       Julien Moura
# Source:       https://github.com/Guts/iso19139_xml_fixer
# Created:      08/09/2017
# -----------------------------------------------------------------------------

# #############################################################################
# ###### Libraries #########
# ##########################

# Standard library
import logging
from logging.handlers import RotatingFileHandler
from os import getcwd, listdir, mkdir, path
import sys
from xml.dom import minidom
from xml.etree import ElementTree as ET

# imports depending on Python version
if sys.version_info < (3, 0):
    from io import open
else:
    pass

# ##############################################################################
# ############ Globals ############
# #################################

# LOG
logger = logging.getLogger("XML_ISO19139_FIXER")
logging.captureWarnings(True)
logger.setLevel(logging.DEBUG)
log_form = logging.Formatter(
    "%(asctime)s || %(levelname)s " "|| %(module)s || %(lineno)s || %(message)s"
)
logfile = RotatingFileHandler("LOG_XML_FIXER.log", "a", 5000000, 1)
logfile.setLevel(logging.DEBUG)
logfile.setFormatter(log_form)
logger.addHandler(logfile)
logger.info("============ START ================")
logger.info("Python version: {}".format(sys.version_info))

# customize script
ds_character_set = "utf-8"
ds_creation_date = "2015-09-08"
ds_srs_code = "urn:ogc:def:crs:EPSG:2154"
ds_license_lbl = "Licence ouverte ETALAB 1.0"
ds_license_url = "http://www.etalab.gouv.fr/licence-ouverte-open-licence"

# #############################################################################
# ########### Classes #############
# #################################


class MetadataXML19139Fixer(object):
    """ISO 19139 XML fixer."""

    def __init__(self):
        """Batch edit input XML files to enhance compliance to ISO19139."""
        self.check_folders()
        self.ns = self.add_namespaces()
        super(MetadataXML19139Fixer, self).__init__()

    def check_folders(self):
        """Check prerequisites."""
        self.fold_in = path.join(getcwd(), "input")
        self.fold_out = path.join(getcwd(), "output")
        # input folder
        if not path.isdir(self.fold_in):
            try:
                mkdir(self.fold_in, 0o777)
            except Exception as e:
                logger.error(e)
                sys.exit()
        else:
            logger.info("Input folder already exists.")
            pass

        # input XML files
        if not len(listdir(self.fold_in)):
            logger.error(
                "Input folder was not created, so "
                "there is not any XML file. Please "
                "copy your XML ISO19139 files inside."
            )
            sys.exit()
        else:
            logger.info("Files are present in input folder.")

        # output folder
        if not path.isdir(self.fold_out):
            try:
                mkdir(self.fold_out, 0o777)
            except Exception as e:
                logger.error(e)
                sys.exit()
        else:
            logger.info("Output folder already exists.")
            pass
        # method ending
        return 0

    def add_namespaces(self):
        """Add ISO19139 namespaces."""
        ns = {
            "gts": "http://www.isotc211.org/2005/gts",
            "gml": "http://www.opengis.net/gml",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "gco": "http://www.isotc211.org/2005/gco",
            "gmd": "http://www.isotc211.org/2005/gmd",
            "gmx": "http://www.isotc211.org/2005/gmx",
            "srv": "http://www.isotc211.org/2005/srv",
            "xl": "http://www.w3.org/1999/xlink",
        }

        # register namespaces
        for namespace in ns:
            ET.register_namespace(namespace, ns.get(namespace))
        return ns

    # -------- Methods to add missing XML parts ------------------------------

    def add_ds_creation_date(self):
        """Add metadata creation date into metadata XML.

        Under /MD_Metadata/identificationInfo/MD_DataIdentification/citation/CI_Citation/date
        <date>
            <CI_Date>
                <date>
                    <gco:Date>2010-07-07Z</gco:Date>
                </date>
                <dateType>
                    <CI_DateTypeCode codeList="http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/codelist/ML_gmxCodelists.xml#CI_DateTypeCode" codeListValue="creation">creation</CI_DateTypeCode>
                </dateType>
            </CI_Date>
        </date>
        """
        ci_citation = self.get_md_ci_citation()
        # creating sub element structure
        parent_date = ET.SubElement(ci_citation, "gmd:date")
        ci_date = ET.SubElement(parent_date, "gmd:CI_date")
        sub_date = ET.SubElement(ci_date, "gmd:date")
        # date value
        value_date = ET.SubElement(sub_date, "gco:date")
        value_date.text = "{}Z".format(ds_creation_date)
        # date type
        sub_date_type = ET.SubElement(ci_date, "gmd:dateType")
        sub_ci_date_typecode = ET.SubElement(sub_date_type, "gmd:CI_DateTypeCode")
        sub_ci_date_typecode.set(
            "codeList",
            "http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/codelist/ML_gmxCodelists.xml#CI_DateTypeCode",
        )
        sub_ci_date_typecode.set("codeListValue", "creation")
        sub_ci_date_typecode.text = "creation"

    def add_md_character_set(self):
        """Add metadata creation date into metadata XML.

        Under /MD_Metadata/characterSet
        AND /MD_Metadata/identificationInfo/MD_DataIdentification/characterSet
        <characterSet>
            <MD_CharacterSetCode codeList="http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/codelist/ML_gmxCodelists.xml#MD_CharacterSetCode" codeListValue="utf8">utf-8</MD_CharacterSetCode>
        </characterSet>
        """
        # metadata root
        char_set = ET.SubElement(self.tpl_root, "gmd:characterSet")
        sub_char_set_code = ET.SubElement(char_set, "gmd:MD_CharacterSetCode")
        sub_char_set_code.set(
            "codeList",
            "http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/codelist/ML_gmxCodelists.xml#MD_CharacterSetCode",
        )
        sub_char_set_code.set("codeListValue", "utf8")
        sub_char_set_code.text = ds_character_set
        # data identification
        md_data_identification = self.get_md_data_identification()
        char_set = ET.SubElement(md_data_identification, "gmd:characterSet")
        sub_char_set_code = ET.SubElement(char_set, "gmd:MD_CharacterSetCode")
        sub_char_set_code.set(
            "codeList",
            "http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/codelist/ML_gmxCodelists.xml#MD_CharacterSetCode",
        )
        sub_char_set_code.set("codeListValue", "utf8")
        sub_char_set_code.text = ds_character_set

    def fix_srs(self):
        """Fix Spatial Reference System.

        Under /MD_Metadata/referenceSystemInfo/MD_ReferenceSystem/referenceSystemIdentifier/RS_Identifier
        <referenceSystemInfo>
            <MD_ReferenceSystem>
                <referenceSystemIdentifier>
                    <RS_Identifier>
                        <code>
                            <gco:CharacterString>urn:ogc:def:crs:EPSG:2154</gco:CharacterString>
                        </code>
                    </RS_Identifier>
                </referenceSystemIdentifier>
            </MD_ReferenceSystem>
        </referenceSystemInfo>
        """
        rs_identifier = self.get_rs_identifier()
        # fix SRS syntax
        code = rs_identifier.find("gmd:code/gco:CharacterString", self.ns)
        code.text = ds_srs_code

        # remove useless codeSpace
        code_space = rs_identifier.find("gmd:codeSpace", self.ns)
        rs_identifier.remove(code_space)

    def fix_cgus(self):
        """Add dataset usage conditions and limitations into metadata XML.

        Under /MD_Metadata/identificationInfo/MD_DataIdentification/resourceConstraints

        <resourceConstraints>
            <MD_Constraints>
                <useLimitation>
                    <gmx:Anchor xl:href="http://www.etalab.gouv.fr/licence-ouverte-open-licence" xl:title="Licence ouverte ETALAB 1.0" />
                </useLimitation>
                <useLimitation>
                    <gco:CharacterString>Conditions sur [geopaysdebrest.fr &gt; Usage des données](https://geo.pays-de-brest.fr/usages/Pages/default.aspx).</gco:CharacterString>
                </useLimitation>
            </MD_Constraints>
        </resourceConstraints>
        <resourceConstraints>
            <MD_LegalConstraints>
                <useLimitation>
                    <gco:CharacterString>Pas de restriction d’accès public selon INSPIRE</gco:CharacterString>
                </useLimitation>
                <useLimitation>
                    <gco:CharacterString>Conditions sur [geopaysdebrest.fr &gt; Usage des données](https://geo.pays-de-brest.fr/usages/Pages/default.aspx).</gco:CharacterString>
                </useLimitation>
                <accessConstraints>
                    <MD_RestrictionCode codeList="http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/codelist/gmxCodelists.xml#MD_RestrictionCode" codeListValue="license">license</MD_RestrictionCode>
                </accessConstraints>
            </MD_LegalConstraints>
        </resourceConstraints>
        """
        rs_ident = self.get_md_data_identification()
        rs_constraints = self.get_rs_constraints()
        # clean up before adding
        if rs_constraints:
            for i in rs_constraints:
                rs_ident.remove(i)
        else:
            pass
        # add new constraints
        constraint_use = ET.SubElement(rs_ident, "gmd:resourceConstraints")
        md_constraint = ET.SubElement(constraint_use, "gmd:MD_Constraints")
        use_limit = ET.SubElement(md_constraint, "gmd:useLimitation")
        use_anchor = ET.SubElement(
            use_limit, "{http://www.isotc211.org/2005/gmx}Anchor"
        )
        use_anchor.set("{http://www.w3.org/1999/xlink}title", ds_license_lbl)
        use_anchor.set("{http://www.w3.org/1999/xlink}href", ds_license_url)

    # -------- Methods to get XML parts --------------------------------------

    def get_md_data_identification(self):
        """Get Character_set level items."""
        pth_character_set = "gmd:identificationInfo/" "gmd:MD_DataIdentification"
        return self.tpl_root.find(pth_character_set, self.ns)

    def get_md_ci_citation(self):
        """Get CI_Citation level items."""
        pth_ci_citation = (
            "gmd:identificationInfo/"
            "gmd:MD_DataIdentification/"
            "gmd:citation/gmd:CI_Citation"
        )
        return self.tpl_root.find(pth_ci_citation, self.ns)

    def get_rs_identifier(self):
        """Get RS_Identifier level items."""
        pth_rs_identifer = (
            "gmd:referenceSystemInfo/"
            "gmd:MD_ReferenceSystem/"
            "gmd:referenceSystemIdentifier/"
            "gmd:RS_Identifier"
        )
        return self.tpl_root.find(pth_rs_identifer, self.ns)

    def get_rs_constraints(self):
        """Get resourceConstraints level items."""
        pth_rs_constraints = (
            "gmd:identificationInfo/"
            "gmd:MD_DataIdentification/"
            "gmd:resourceConstraints"
        )
        return self.tpl_root.findall(pth_rs_constraints, self.ns)

    # -------- XML utils ----------------------------------------------------

    def prettify(self, elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


# #############################################################################
# ### Stand alone execution #######
# #################################

if __name__ == "__main__":
    """Test parameters for a stand-alone run."""
    app = MetadataXML19139Fixer()
    for xml in listdir(app.fold_in):
        logger.info(xml)
        # opening the input
        with open(path.join(app.fold_in, xml), "r", encoding="utf-8") as in_xml:
            # parser
            app.tpl = ET.parse(in_xml)
            # getting the elements and sub-elements structure
            app.tpl_root = app.tpl.getroot()
            # fixes
            app.add_ds_creation_date()  # creation date
            app.add_md_character_set()  # character set
            app.fix_srs()  # SRS
            app.fix_cgus()  # CGUs

            # # namespaces
            # for ns in app.ns:
            #     ET.register_namespace(ns, app.ns.get(ns))
            # saving the output xml file
            app.tpl.write(
                path.join(app.fold_out, xml),
                encoding="utf-8",
                xml_declaration=1,
                # default_namespace=app.ns.get("gmd"),
                method="xml",
            )
