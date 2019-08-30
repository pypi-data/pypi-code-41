"""Provides the BaseProvider base class"""
import re
from marshmallow import Schema, fields, validate

from ..provider import BaseProvider
from ..provider import BaseProviderSchema

SWAP_SIZE_REGEX = re.compile('^[1-9]+\d*[KGMT]$')


class BaseComputeConfigSchema(Schema):
    """ Base schema to be extended in Compute implementations"""
    queue_threshold = fields.Number(required=True)
    max_compute = fields.Number(required=True)
    machine_type = fields.String(required=True,
                                 allow_none=False,
                                 validate=validate.Length(min=1))
    disk_size = fields.Number(required=True)
    swap_size = fields.String(default='30G',
                              validate=validate.Regexp(SWAP_SIZE_REGEX))
    preemptible = fields.Boolean(required=True)
    zone = fields.String(required=True, allow_none=True)
    region = fields.String(required=True,
                           allow_none=False,
                           validate=validate.Length(min=1))

    def __init__(self, strict=True, **kwargs):
        super(BaseComputeConfigSchema, self).__init__(strict=strict, **kwargs)


class BaseComputeSchema(BaseProviderSchema):
    """Schema definition for the object"""
    config = fields.Nested(BaseComputeConfigSchema, many=False, required=True)


class BaseComputeProvider(BaseProvider):
    """The base compute provider object.
    Provides configuration and validation interface for compute types"""
    # The schema for validating configuration (required)
    # This will be overridden in actual implementations
    _schema = None

    config = None
    creds = None

    def __init__(self, **kwargs):
        """Initializes this class with the given configuration

        Args:
            creds (Creds): The provider credentials object
            config (dict): The configuration object for storage
        """
        super(BaseComputeProvider, self).__init__(**kwargs)
