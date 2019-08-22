"""DataSourceGroupVersion module class"""

from ..apis.data_source_group_version_api import DataSourceGroupVersionApi
from ..common.base import Base
from ..common.config import *

MODULE_NAME = DATA_SOURCE_GROUP_VERSION


class DataSourceGroupVersion(DataSourceGroupVersionApi):
    FLG_STATUS_DEPLOYED = 'D'

    def __init__(self,
                 name, identifier,
                 flg_available, description=''):
        self.id = None
        self.name = name
        self.identifier = identifier
        self.flg_available = flg_available
        self.description = description

    @staticmethod
    def get(mdc_client, data_source_group_id, version_name):
        response = mdc_client.get_data_source_group_version_api(
            data_source_group_id, version_name)
        Base.cal_debug(MODULE_NAME, 'get', response)

        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def update(mdc_client, id, params):
        response = mdc_client.update_data_source_group_version_api(id, params)
        Base.cal_debug(MODULE_NAME, 'get', response)

        return Base.format_response(response, GET, OK, MODULE_NAME)
