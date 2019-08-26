import io
import struct

import fastavro

from glutemulo.errors import ValidationError, SerializerError


class ContextStringIO(io.BytesIO):
    """
    Wrapper to allow use of StringIO via 'with' constructs.
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False


MAGIC_BYTE = 0


class FastAvroEncoder:
    def __init__(self, schema, schema_id, validate=True):
        """
        Creates a encoder object.
        :param int schema_id: schema integer ID
        :param dict schema: schema dict
        :param bool validate: do validation flag
        :returns: encoded data
        :rtype: binary string
        """
        self.shema_id = schema_id
        self.validate = validate
        self.parsed_schema = fastavro.parse_schema(schema)
        self.schema_id_bytes = struct.pack(">I", schema_id)

    def encode(self, message):
        """
        Encode a record using object with a given schema id. The record must
        be a python dictionary.
        :param int schema_id: integer ID
        :param dict message: An object to serialize
        :returns: encoded data
        :rtype: binary string
        """
        if self.validate:
            try:
                fastavro.validation.validate(message, self.parsed_schema)
            except fastavro.validation.ValidationError as error:
                raise ValidationError(f"Validation error: {error.args[0]}")

        with ContextStringIO() as outf:
            outf.write(struct.pack("b", MAGIC_BYTE))
            outf.write(self.schema_id_bytes)  # schema id
            fastavro.schemaless_writer(outf, self.parsed_schema, message)
            return outf.getvalue()


class FastAvroMultipleSchemaDecoder:
    def __init__(self, schema_registry):
        self._schema_registry = schema_registry

    def decode(self, record):
        with ContextStringIO(record) as buf:
            magic, schema_id = struct.unpack(">bI", buf.read(5))
            if magic != MAGIC_BYTE:
                raise SerializerError("record does not start with magic byte")

            schema = self._schema_registry.get_by_id(schema_id)
            return fastavro.schemaless_reader(buf, schema)


class SchemaRegistry:
    def get_by_id(self, id):
        raise Exception('Not implemented')


class LocalSchemaRegistry:
    def __init__(self, schemas):
        self._schema_cache = {id_: fastavro.parse_schema(schema) for id_, schema in schemas.items()}

    def get_by_id(self, id):
        return self._schema_cache[id]

# TODO: Implemente a client for a remote registry using requests

class FastAvroDecoder(FastAvroMultipleSchemaDecoder):
    def __init__(self, schema_id, schema):
        self.registry = LocalSchemaRegistry({schema_id: schema})
        super().__init__(self.registry)
