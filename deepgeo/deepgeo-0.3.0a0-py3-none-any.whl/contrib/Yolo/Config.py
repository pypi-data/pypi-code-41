import json
from deepgeo.util import create, polygon

class Config:
    def __init__(self):
        self.VERSION = ""
        self.MEMO = ""
        self.MODEL_FILE_NAME = ""
        self.MODEL_PATH = ""
        self.CATEGORY = ""
        self.CONFIG = ""

    def _to_json_(self):
        """
            # _to_json_ : 설정 정보를 json 데이터로 반환합니다.
        """
        data = {}
        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                data[a] = getattr(self, a)
        return data

    def get_value(self, key):
        return getattr(self, key)

    def load_config(self, data):
        """
            # load_config : config 데이터를 json이나 경로를 입력하면 해당 정보에 맞게 데이터를 조정합니다.

            data : json 파일의 경로나, json 데이터를 받습니다.
        """
        assert data is not None or data != "", "load_config : data is None"
        config=None
        if isinstance(data, str):
            with open(data) as data_file:
                config = json.load(data_file)
        else:
            config = data
        keys = list(config.keys())

        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                if a in keys:
                    setattr(self,a,config[a])

        del config
        del keys
    
    def set_config(self, option:str, value, re_setting=True):
        """
            # set_config : 특정 Key값의 데이터를 변경합니다.

            option : 변경하고자 하는 Key값을 입력합니다. 
            -------------------------------------
            value : 변경할 데이터를 입력합니다.
            -------------------------------------
            re_setting : 연관데이터를 갱신 할 것인지 여부입니다. 
        """
        setattr(self,option,value)
        if re_setting is True:
            super().__init__()

    def save_config(self, path:str, file_name:str):
        """
            # save_config : 설정 데이터를 json 파일 형태로 저장합니다.

            path : 저장할 경로를 입력합니다. 
            -------------------------------------
            file_name : 저장할 파일 명을 입력합니다. 
        """
        assert path is not None or path != "", "save_config : path is None"
        assert file_name is not None or file_name != "", "save_config : file_name is None"

        path = create.folder(path)
        file_name = file_name.replace("."+file_name.split(".")[-1],"")
        path = path + file_name + ".json"
        data = self._to_json_()
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent='\t', sort_keys=True, default=polygon.from_numpy)
        del file_name
        del data
        return path

    def display(self):
        print(self._to_json_())