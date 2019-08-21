"""DataGroupApi module class"""

import json

from ..common.base import Base


class DataGroupApi(Base):
    def create_data_group_api(self, data_group):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(data_group))

    def delete_data_group_api(self, data_group_id):
        api_url = self.__get_api_url(data_group_id)
        return self.api_delete(api_url)

    def update_data_group_api(self, data_group_id, data_group):
        api_url = self.__get_api_url(data_group_id)
        return self.api_put(api_url, data=json.dumps(data_group))

    def get_data_group_by_id_api(self, data_group_id):
        api_url = self.__get_api_url(data_group_id)
        return self.api_get(api_url, params={})

    def get_all_data_groups_by_name_api(self, name):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'name': name})

    def get_all_data_groups_by_experiment_id_api(self, experiment_id):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'experiment_id': experiment_id})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'data_groups/'
        return self.get_api_url(model_name, api_specifics)
