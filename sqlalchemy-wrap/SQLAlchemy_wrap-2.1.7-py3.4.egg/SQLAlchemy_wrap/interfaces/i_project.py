import typing
from abc import abstractmethod
from .i_table import ITable


class IProject(ITable):

    @abstractmethod
    def update_or_insert(self, sample_id: str, content: dict):
        """
            if the current sample id is exists, it will update. otherwise insert new record
        :param sample_id:
        :param content: the content you want to insert
        :return:
        """
        pass

    @abstractmethod
    def get_by_sample_id(self, sample_id: str) -> dict:
        """
        :param sample_id: current project sample id
        :return: if the sample_id is exists, the dict that contain current project data,
                 like "{'small_data':"small_data_value',....}", otherwise return {}
        """
        pass

    @abstractmethod
    def remove_by_sample_id(self, sample_id: str):
        pass

    @abstractmethod
    def insert_by_sample_id(self, sample_id: str, content: dict):
        pass

    @abstractmethod
    def sample_id_exists(self, sample_id: str) -> bool:
        pass

    @abstractmethod
    def search(self, sample_id: str = 0, operator: str = "", started: str = "",
               finished: str = "", fields: typing.List[str] = None) -> typing.List[dict]:
        pass
