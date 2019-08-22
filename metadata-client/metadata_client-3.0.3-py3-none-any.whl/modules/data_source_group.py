"""DataSourceGroup module class"""

from ..apis.data_source_group_api import DataSourceGroupApi
from ..common.base import Base
from ..common.config import *

MODULE_NAME = DATA_SOURCE_GROUP


class DataSourceGroup(DataSourceGroupApi):
    def __init__(self,
                 name, identifier,
                 flg_available, description=''):
        self.id = None
        self.name = name
        self.identifier = identifier
        self.flg_available = flg_available
        self.description = description

    @staticmethod
    def get_by_name(mdc_client, name):
        response = mdc_client.get_data_source_group_by_name_api(name)
        Base.cal_debug(MODULE_NAME, 'get_by_name', response)

        return Base.format_response(response, GET, OK, MODULE_NAME)
