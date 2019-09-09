from abc import ABC, abstractmethod
import json

class SQLClient(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def switch_to(self, db_object, db_object_name):
        pass

    @abstractmethod
    def dml_query(self, query_string):
        pass

    @abstractmethod
    def select_query(self, query_string):
        pass

    def _load_configuration_file(self , configuration_file_path):
        with open(configuration_file_path ,'r') as config_file:
            return json.load(config_file , strict = False)
