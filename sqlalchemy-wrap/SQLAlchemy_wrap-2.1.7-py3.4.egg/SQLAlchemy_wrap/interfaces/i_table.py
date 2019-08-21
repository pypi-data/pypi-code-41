from abc import ABCMeta, abstractmethod
import typing


class ITable(metaclass=ABCMeta):
    pass
    # @abstractmethod
    # def count(self) -> int:
    #     """
    #         get the total number of the collection/table records
    #     :return: total number
    #     """
    #     pass
    #
    # @abstractmethod
    # def update(self, condition: dict, update_content: dict):
    #     pass
    #
    # @abstractmethod
    # def insert(self, document: dict):
    #     pass
    #
    # @abstractmethod
    # def remove(self, condition: dict = None):
    #     pass
    #
    # @abstractmethod
    # def get(self, condition: dict = None) -> typing.List[dict]:
    #     """
    #         get list contain record that meet condition
    #     :param condition:
    #     :return: ist, if there is no record, it will return []
    #     """
    #     pass
    #
    # @abstractmethod
    # def get_all(self) -> typing.List[dict]:
    #     """
    #         get all records
    #     :return: list, if there is no record, it will return []
    #     """
    #     pass
