# -*- coding: utf-8 -*-
import msgpack
from missinglink.core.avro_utils import AvroWriter
from missinglink.legit.file_hash_generator import FileHashGenerator
from .metadata_validator import MetadataValidator
import tempfile
from .path_utils import StorageType


class InvalidMetadataFile(object):
    def __init__(self, filename, errors):
        self.filename = filename
        self.errors = errors


class IndexMetadataInfoGenerator(object):
    def __init__(self, skip_metadata, is_embedded_mode, existing_metadata_fields=None):
        self._total_data_files = 0
        self._total_size_data_files = 0

        self._skip_metadata = skip_metadata
        self._is_embedded_mode = is_embedded_mode

        if not self._skip_metadata:
            self._metadata_schema = {}
            self._metadata_errors = []
            self._msg_pack_metadata_file = tempfile.TemporaryFile('wb+')

            existing_metadata_fields = existing_metadata_fields or []
            self._existing_metadata_fields_mapping = {f.lower(): f for f in existing_metadata_fields}
            self._existing_metadata_fields_lowercase = set(self._existing_metadata_fields_mapping.keys())
        else:
            self._metadata_schema = None
            self._metadata_errors = None
            self._msg_pack_metadata_file = None
            self._existing_metadata_fields_mapping = {}
            self._existing_metadata_fields_lowercase = set()

        self._index_schema = {}
        self._msg_pack_index_file = tempfile.TemporaryFile('wb+')

    @staticmethod
    def get_metadata_errors(data, rel_file_name, metadata_schema):
        metadata_validator = MetadataValidator(data, metadata_schema)
        errors = metadata_validator.get_validation_errors()
        if len(errors) > 0:
            return InvalidMetadataFile(rel_file_name, errors)

    def _merge_existing_metadata_fields(self, data):
        fields_lowercase_mapping = {f.lower(): f for f in data.keys()}
        fields_lowercase = set(fields_lowercase_mapping.keys())
        merged_fields_lowercase = fields_lowercase & self._existing_metadata_fields_lowercase
        new_fields_lowercase = fields_lowercase - self._existing_metadata_fields_lowercase

        for field_lowercase in merged_fields_lowercase:
            original_field_name = fields_lowercase_mapping[field_lowercase]
            existing_field_name = self._existing_metadata_fields_mapping[field_lowercase]
            field_value = data.pop(original_field_name)
            data[existing_field_name] = field_value

        for new_field_lowercase in new_fields_lowercase:
            self._existing_metadata_fields_lowercase.add(new_field_lowercase)
            self._existing_metadata_fields_mapping[new_field_lowercase] = fields_lowercase_mapping[new_field_lowercase]

        return data

    def _handle_metadata_entry(self, data, rel_file_name):
        file_metadata_errors = self.get_metadata_errors(data, rel_file_name, self._metadata_schema)
        if file_metadata_errors is not None:
            self._metadata_errors.append(file_metadata_errors)
            return

        data = self._merge_existing_metadata_fields(data)

        self._msg_pack_metadata_file.write(msgpack.packb((rel_file_name, data), use_bin_type=True))
        AvroWriter.get_schema_from_item(self._metadata_schema, data)

    @classmethod
    def __append_index_file(cls, file_info, is_embedded_mode):

        is_local_fs = file_info.get('sys') == StorageType.Local
        file_path = file_info['path']
        file_size = file_info['size']
        mtime = file_info['mtime']
        ctime = file_info.get('ctime', mtime)
        mode = file_info.get('mode', 0)

        params = {
            'ctime': ctime,
            'mtime': mtime,
            'size': file_size,
            'mode': mode,
        }

        if 'sha' in file_info:
            params['sha'] = file_info['sha']
        else:
            should_hash_file_stats = is_local_fs and not is_embedded_mode

            sha = FileHashGenerator.hash_file(
                file_name=file_path,
                st_mtime=mtime,
                st_size=file_size,
                should_hash_file_stats=should_hash_file_stats
            )

            params['sha'] = sha

        if 'url' in file_info:
            params['url'] = file_info['url']

        return params

    def _handle_entry(self, entry_type, rel_file_name, data):
        from .data_sync import DataSync

        if entry_type == DataSync.EntryType.Metadata:
            self._handle_metadata_entry(data, rel_file_name)
            return

        self._total_size_data_files += data['size']
        self._total_data_files += 1

        file_params = self.__append_index_file(data, self._is_embedded_mode)
        AvroWriter.get_schema_from_item(self._index_schema, file_params)
        self._msg_pack_index_file.write(msgpack.packb((rel_file_name, file_params), use_bin_type=True))

    def generate(self, files_info_iter, stop_on_first_error=True):
        for entry_type, rel_file_name, data in files_info_iter:
            self._handle_entry(entry_type, rel_file_name, data)
            if stop_on_first_error and self._metadata_errors:
                break

        self._msg_pack_index_file.seek(0)

        if not self._skip_metadata:
            self._msg_pack_metadata_file.seek(0)

        metadata_info = self._msg_pack_metadata_file, self._metadata_schema, self._metadata_errors

        index_info = self._msg_pack_index_file, self._total_data_files, self._total_size_data_files, self._index_schema

        return index_info, metadata_info
