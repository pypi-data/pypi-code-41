# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
from xml.dom import minidom
from lxml import (
    etree,
    isoschematron
)
from tempfile import NamedTemporaryFile
import os
from io import BytesIO

# project
from .defaults import Defaults
from . import xml_parse
from .command import Command
from .logger import log

from .exceptions import (
    KiwiSchemaImportError,
    KiwiValidationError,
    KiwiDescriptionInvalid,
    KiwiDataStructureError,
    KiwiDescriptionConflict,
    KiwiExtensionError,
    KiwiCommandNotFound
)


class XMLDescription(object):
    """
    **Implements data management for the XML description**

    * XSLT Style Sheet processing to apply on this version of kiwi
    * Schema Validation based on RelaxNG schema
    * Loading XML data into internal data structures

    Attributes

    :param string description: path to XML description file
    :param string derived_from: path to base XML description file
    :param string xml_content: XML description data as content string
    """
    def __init__(self, description=None, derived_from=None, xml_content=None):
        if description and xml_content:
            raise KiwiDescriptionConflict(
                'description and xml_content are mutually exclusive'
            )
        self.description_xslt_processed = NamedTemporaryFile()
        self.derived_from = derived_from

        self.description = description
        self.xml_content = xml_content
        self.extension_data = {}

    def load(self):                                         # noqa: C901
        """
        Read XML description, pass it along to the XSLT processor,
        validate it against the schema and finally pass it to the
        autogenerated(generateDS) parser.

        :return: instance of XML toplevel domain (image)

        :rtype: object
        """
        try:
            self._xsltproc()
            schema_doc = etree.parse(Defaults.get_schema_file())
            relaxng = etree.RelaxNG(schema_doc)
            schematron = isoschematron.Schematron(
                schema_doc, store_report=True
            )
        except Exception as e:
            raise KiwiSchemaImportError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        try:
            description = etree.parse(self.description_xslt_processed.name)
            validation_rng = relaxng.validate(description)
            validation_sch = schematron.validate(description)
        except Exception as e:
            raise KiwiValidationError(
                '%s: %s' % (type(e).__name__, format(e))
            )
        if not validation_rng:
            self._get_relaxng_validation_details(
                Defaults.get_schema_file(),
                self.description_xslt_processed.name
            )
        if not validation_sch:
            self._get_schematron_validation_details(
                schematron.validation_report
            )
        if not validation_rng or not validation_sch:
            if self.description:
                message = 'Schema validation for {description} failed'.format(
                    description=self.description
                )
            else:
                message = 'Schema validation for XML content failed'
            raise KiwiDescriptionInvalid(message)

        parse_result = self._parse()

        if parse_result.get_extension():
            extension_namespace_map = \
                description.getroot().xpath('extension')[0].nsmap

            for namespace_name in extension_namespace_map:
                extensions_for_namespace = description.getroot().xpath(
                    'extension/{namespace}:*'.format(namespace=namespace_name),
                    namespaces=extension_namespace_map
                )
                if extensions_for_namespace:
                    # one toplevel entry point per extension via xmlns
                    if len(extensions_for_namespace) > 1:
                        raise KiwiExtensionError(
                            'Multiple toplevel sections for "{0}" found'.format(
                                namespace_name
                            )
                        )

                    # store extension xml data parse tree for this namespace
                    self.extension_data[namespace_name] = \
                        etree.ElementTree(extensions_for_namespace[0])

                    # validate extension xml data
                    try:
                        xml_catalog = Command.run(
                            [
                                'xmlcatalog', '/etc/xml/catalog',
                                extension_namespace_map[namespace_name]
                            ]
                        )
                        extension_schema = xml_catalog.output.rstrip().replace(
                            'file://', ''
                        )
                        extension_relaxng = etree.RelaxNG(
                            etree.parse(extension_schema)
                        )
                    except Exception as e:
                        raise KiwiExtensionError(
                            'Extension schema error: {0}: {1}'.format(
                                type(e).__name__, e
                            )
                        )
                    validation_result = extension_relaxng.validate(
                        self.extension_data[namespace_name]
                    )
                    if not validation_result:
                        xml_data_unformatted = etree.tostring(
                            self.extension_data[namespace_name],
                            encoding='utf-8'
                        )
                        xml_data_domtree = minidom.parseString(
                            xml_data_unformatted
                        )
                        extension_file = NamedTemporaryFile()
                        with open(extension_file.name, 'w') as xml_data:
                            xml_data.write(xml_data_domtree.toprettyxml())
                        self._get_relaxng_validation_details(
                            extension_schema, extension_file.name
                        )
                        raise KiwiExtensionError(
                            'Schema validation for extension XML data failed'
                        )

        return parse_result

    def get_extension_xml_data(self, namespace_name):
        """
        Return the xml etree parse result for the specified extension namespace

        :param string namespace_name: name of the extension namespace

        :return: result of etree.parse

        :rtype: object
        """
        if namespace_name in self.extension_data:
            return self.extension_data[namespace_name]

    def _get_relaxng_validation_details(self, schema_file, description_file):
        """
        Run jing program to validate description against the schema

        Jing provides detailed error information in case of a schema
        validation failure
        """
        try:
            cmd = Command.run(
                ['jing', schema_file, description_file],
                raise_on_error=False
            )
        except KiwiCommandNotFound as e:
            log.info(
                'For detailed schema validation report, please install: jing'
            )
            log.info(
                '%s: %s: %s', 'jing', type(e).__name__, format(e)
            )
            return
        log.info('RelaxNG validation failed. See jing report:')
        log.info('--> %s', cmd.output)

    def _get_schematron_validation_details(self, validation_report):
        """
        Extract error message form the schematron validation report

        :param etree validation_report: the schematron validation report
        """
        nspaces = validation_report.getroot().nsmap
        log.info('Schematron validation failed:')
        for msg in validation_report.xpath(
            '//svrl:failed-assert/svrl:text', namespaces=nspaces
        ):
            log.info('--> %s', msg.text)

    def _parse(self):
        try:
            parse = xml_parse.parse(
                self.description_xslt_processed.name, True
            )
            parse.description_dir = self.description and os.path.dirname(
                self.description
            )
            parse.derived_description_dir = self.derived_from
            return parse
        except Exception as e:
            raise KiwiDataStructureError(
                '%s: %s' % (type(e).__name__, format(e))
            )

    def _xsltproc(self):
        """
        Apply XSLT style sheet rules to the XML data

        The result of the XSLT processing is stored in a named
        temporary file and used for further schema validation
        and parsing into the data structure classes
        """
        xslt_transform = etree.XSLT(
            etree.parse(Defaults.get_xsl_stylesheet_file())
        )

        xml_source = self.description if self.description else \
            BytesIO(bytes(self.xml_content))

        with open(self.description_xslt_processed.name, "wb") as xsltout:
            xsltout.write(
                etree.tostring(xslt_transform(etree.parse(xml_source)))
            )
