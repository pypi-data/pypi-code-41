import csv
import json
import logging
import os
import re
from collections import OrderedDict
from io import BytesIO, StringIO
from zipfile import ZipFile
from urllib.parse import urljoin

import json_merge_patch
import requests

from .codelist import Codelist
from .extension_registry import ExtensionRegistry
from .extension_version import ExtensionVersion
from .util import json_loads

logger = logging.getLogger('ocdsextensionregistry')


class ProfileBuilder:
    def __init__(self, standard_tag, extension_versions, registry_base_url=None, schema_base_url=None):
        """
        Accepts an OCDS version and either a dictionary of extension identifiers and versions, or a list of extensions'
        metadata URLs, base URLs and/or download URLs, and initializes a reader of the extension registry.

        :param str standard_tag: the OCDS version tag, e.g. ``'1__1__3'``
        :param extension_versions: the extension versions
        :param str registry_base_url: the registry's base URL, defaults to
                                      ``'https://raw.githubusercontent.com/open-contracting/extension_registry/master/'``
        :param str schema_base_url: the schema's base URL, e.g.
                                    ``'https://standard.open-contracting.org/profiles/ppp/schema/1__0__0__beta/'``
        :type extension_versions: dict or list
        :
        """
        self.standard_tag = standard_tag
        self.extension_versions = extension_versions
        self.schema_base_url = schema_base_url
        self._file_cache = {}

        # Allows setting the registry URL to e.g. a pull request, when working on a profile.
        if not registry_base_url:
            registry_base_url = 'https://raw.githubusercontent.com/open-contracting/extension_registry/master/'

        self.registry = ExtensionRegistry(registry_base_url + 'extension_versions.csv')

    def extensions(self):
        """
        Returns the matching extension versions from the registry.
        """
        if isinstance(self.extension_versions, dict):
            for identifier, version in self.extension_versions.items():
                yield self.registry.get(id=identifier, version=version)
        else:
            for url in self.extension_versions:
                data = dict.fromkeys(['Id', 'Date', 'Version', 'Base URL', 'Download URL'])
                if url.endswith('/extension.json'):
                    data['Base URL'] = url[:-14]
                elif url.endswith('/'):
                    data['Base URL'] = url
                else:
                    data['Download URL'] = url
                yield ExtensionVersion(data)

    def release_schema_patch(self, extension_field=None):
        """
        Returns the consolidated release schema patch.

        :param str extension_field: the schema field with which to annotate all definitions and properties with
                                    extension names
        """
        output = OrderedDict()

        # Replaces `null` with sentinel values, to preserve the null'ing of fields by extensions in the final patch.
        for extension in self.extensions():
            patch = json_loads(re.sub(r':\s*null\b', ': "REPLACE_WITH_NULL"', extension.remote('release-schema.json')))
            if extension_field:
                _add_extension_field(patch, extension.metadata['name']['en'], extension_field)
            json_merge_patch.merge(output, patch)

        return json_loads(json.dumps(output).replace('"REPLACE_WITH_NULL"', 'null'))

    def patched_release_schema(self, extension_field=None):
        """
        Returns the patched release schema.

        :param str extension_field: the schema field with which to annotate all definitions and properties with
                                    extension names
        """
        output = json_loads(self.get_standard_file_contents('release-schema.json'))
        json_merge_patch.merge(output, self.release_schema_patch(extension_field=extension_field))
        if self.schema_base_url:
            output['id'] = urljoin(self.schema_base_url, 'release-schema.json')

        return output

    def release_package_schema(self):
        """
        Returns a release package schema. If `schema_base_url` was provided, updates schema URLs.
        """
        data = json_loads(self.get_standard_file_contents('release-package-schema.json'))

        if self.schema_base_url:
            data['id'] = urljoin(self.schema_base_url, 'release-package-schema.json')
            data['properties']['releases']['items']['$ref'] = urljoin(self.schema_base_url, 'release-schema.json')

        return data

    def standard_codelists(self):
        """
        Returns the standard's codelists as Codelist objects.
        """
        codelists = OrderedDict()

        # Populate the file cache.
        self.get_standard_file_contents('release-schema.json')

        # This method shouldn't need to know about `_file_cache`.
        for path, content in self._file_cache.items():
            name = os.path.basename(path)
            if 'codelists' in path.split(os.sep) and name:
                codelists[name] = Codelist(name)
                codelists[name].extend(csv.DictReader(StringIO(content)), 'OCDS Core')

        return list(codelists.values())

    def extension_codelists(self):
        """
        Returns the extensions' codelists as Codelist objects.

        The extensions' codelists may be new, or may add codes to (+name.csv), remove codes from (-name.csv) or replace
        (name.csv) the codelists of the standard or other extensions.

        Codelist additions and removals are merged across extensions. If new codelists or codelist replacements differ
        across extensions, an error is raised.
        """
        codelists = OrderedDict()

        # Keep the original content of codelists, to compare across extensions.
        originals = {}

        for extension in self.extensions():
            # We use the "codelists" field in extension.json (which standard-maintenance-scripts validates). An
            # extension is not guaranteed to offer a download URL, which is the only other way to get codelists.
            for name in extension.metadata.get('codelists', []):
                content = extension.remote('codelists/' + name)

                if name not in codelists:
                    codelists[name] = Codelist(name)
                    originals[name] = content
                elif not codelists[name].patch:
                    assert originals[name] == content, 'codelist {} differs across extensions'.format(name)
                    continue

                codelists[name].extend(csv.DictReader(StringIO(content)), extension.metadata['name']['en'])

        # If a codelist replacement (name.csv) is consistent with additions (+name.csv) and removals (-name.csv), the
        # latter should be removed. In other words, the expectations are that:
        #
        # * A codelist replacement shouldn't omit added codes.
        # * A codelist replacement shouldn't include removed codes.
        # * If codes are added after a codelist is replaced, this should result in duplicate codes.
        # * If codes are removed after a codelist is replaced, this should result in no change.
        #
        # If these expectations are not met, an error is raised. As such, profile authors only have to handle cases
        # where codelist modifications are inconsistent across extensions.
        for codelist in list(codelists.values()):
            basename = codelist.basename
            if codelist.patch and basename in codelists:
                name = codelist.name
                codes = codelists[basename].codes
                if codelist.addend:
                    for row in codelist:
                        code = row['Code']
                        assert code in codes, '{} added by {}, but not in {}'.format(code, name, basename)
                    logger.info('{0} has the codes added by {1} - ignoring {1}'.format(basename, name))
                else:
                    for row in codelist:
                        code = row['Code']
                        assert code not in codes, '{} removed by {}, but in {}'.format(code, name, basename)
                    logger.info('{0} has no codes removed by {1} - ignoring {1}'.format(basename, name))
                del codelists[name]

        return list(codelists.values())

    def patched_codelists(self):
        """
        Returns patched and new codelists as Codelist objects.
        """
        codelists = OrderedDict()

        for codelist in self.standard_codelists():
            codelists[codelist.name] = codelist

        for codelist in self.extension_codelists():
            if codelist.patch:
                basename = codelist.basename
                if codelist.addend:
                    # Add the rows.
                    codelists[basename].rows.extend(codelist.rows)
                    # Note that the rows may not all have the same columns, but DictWriter can handle this.
                else:
                    # Remove the codes. Multiple extensions can remove the same codes.
                    removed = codelist.codes
                    codelists[basename].rows = [row for row in codelists[basename] if row['Code'] not in removed]
            else:
                # Set or replace the rows.
                codelists[codelist.name] = codelist

        return list(codelists.values())

    def get_standard_file_contents(self, basename):
        """
        Returns the contents of the file within the standard.

        Downloads the given version of the standard, and caches the contents of files in the schema/ directory.
        """
        if not self._file_cache:
            url = 'https://codeload.github.com/open-contracting/standard/zip/' + self.standard_tag
            response = requests.get(url)
            response.raise_for_status()
            zipfile = ZipFile(BytesIO(response.content))
            names = zipfile.namelist()
            path = 'standard/schema/'
            start = len(names[0] + path)
            for name in names[1:]:
                if path in name:
                    self._file_cache[name[start:]] = zipfile.read(name).decode('utf-8')

        return self._file_cache[basename]


def _add_extension_field(schema, extension_name, field_name, pointer=None):
    if pointer is None:
        pointer = ()
    if isinstance(schema, list):
        for item in schema:
            _add_extension_field(item, extension_name, field_name=field_name, pointer=pointer)
    elif isinstance(schema, dict):
        if len(pointer) > 1 and pointer[-2] in ('definitions', 'properties'):
            schema[field_name] = extension_name
        for key, value in schema.items():
            _add_extension_field(value, extension_name, field_name=field_name, pointer=pointer + (key,))
