"""Instrument module class"""

from ..apis.instrument_api import InstrumentApi
from ..common.base import Base
from ..common.config import *

MODULE_NAME = INSTRUMENT


class Instrument(InstrumentApi):
    def __init__(self, metadata_client,
                 name, identifier, url,
                 facility_id, instrument_type_id, repository_id,
                 flg_available, description=''):
        self.metadata_client = metadata_client
        self.id = None
        self.name = name
        self.identifier = identifier
        self.url = url
        self.facility_id = facility_id
        self.instrument_type_id = instrument_type_id
        self.repository_id = repository_id
        self.flg_available = flg_available
        self.description = description

    @staticmethod
    def get_by_id(mdc_client, instrument_id):
        response = mdc_client.get_instrument_by_id_api(instrument_id)

        Base.cal_debug(MODULE_NAME, 'get_by_id', response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_all_by_facility_id(mdc_client, facility_id):
        resp = mdc_client.get_all_instruments_by_facility_id_api(facility_id)

        Base.cal_debug(MODULE_NAME, 'get_all_by_facility_id', resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    @staticmethod
    def get_all_from_xfel(mdc_client):
        xfel_fac_id = 1
        resp = mdc_client.get_all_instruments_by_facility_id_api(xfel_fac_id)

        Base.cal_debug(MODULE_NAME, 'get_all_from_xfel', resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    @staticmethod
    def get_by_identifier(mdc_client, identifier):
        response = mdc_client.get_all_instruments_by_identifier_api(identifier)
        Base.cal_debug(MODULE_NAME, 'get_by_identifier', response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    def __get_resource(self):
        instrument = {
            MODULE_NAME: {
                'name': self.name,
                'identifier': self.identifier,
                'url': self.url,
                'facility_id': self.facility_id,
                'instrument_type_id': self.instrument_type_id,
                'repository_id': self.repository_id,
                'flg_available': self.flg_available,
                'description': self.description
            }
        }

        return instrument
