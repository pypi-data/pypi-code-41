"""DataFileApi module class"""

import json

from ..common.base import Base


class DataFileApi(Base):
    def create_data_file_api(self, data_file):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(data_file))

    def delete_data_file_api(self, data_file_id):
        api_url = self.__get_api_url(data_file_id)
        return self.api_delete(api_url)

    def update_data_file_api(self, data_file_id, data_file):
        api_url = self.__get_api_url(data_file_id)
        return self.api_put(api_url, data=json.dumps(data_file))

    def get_data_file_by_id_api(self, data_file_id):
        api_url = self.__get_api_url(data_file_id)
        return self.api_get(api_url, params={})

    def search_data_files_api(self, run_number, proposal_number):
        api_url = self.__get_api_url('search_data_files')
        return self.api_get(api_url,
                            params={'run_number': run_number,
                                    'proposal_number': proposal_number})

    def get_all_data_files_by_data_group_id_api(self, data_group_id):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'data_group_id': data_group_id})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'data_files/'
        return self.get_api_url(model_name, api_specifics)
