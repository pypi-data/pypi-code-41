# deepgeo 라이브러리
from deepgeo import Extension
from deepgeo.util import error

# 추가 라이브러리
from contrib_extension import Extension

class Engine(object):
    def __init__(self) -> None:
        self._ext_ = Extension(use_lib_name=deepgeo, category="deepgeo_category")
        self._ext_.importlib("image", False)
        self._ext_.importlib("video", False)
        self._ext_.importlib("frame", False)
        self._model_ = {}

    def _get_model(self, name:str) -> object:
        """등록된 모델을 가져옵니다.

        Args:
            name: 모델을 식별할 수 있는 고유 id 값입니다.

        Returns:
            모델의 객체를 딕셔너리로 반환됩니다.

            예:
            {model_name<:str>:model<:object>}

        Raises:
            KeyNotNoneError: 키 값이 None 일 경우 에러 발생
            KeyNotEmptyError: 키 값이 비어있을 경우 에러 발생
            KeyNoDataError: 찾고자 하는 데이터가 없을 경우 발생
        """
        
        if name is None: raise error.KeyNotNoneError()
        if name == "": raise error.KeyNotEmptyError()
        if not name in list(self._model_.keys()): raise error.KeyNoDataError()

        return self._model_[name]

    def _get_model_class(self, _name:str, _type:str) -> object:
        """등록된 모델의 클래스를 가져옵니다.

        Args:
            _name: 모델을 식별할 수 있는 고유 id 값입니다.
            _type: model/dataset/config 3가지의 기본 클래스를 지정합니다.

        Returns:
            요청한 이름의 클래스를 반환합니다.
            _type에 벗어난 데이터는 None을 반환합니다.

        Raises:
            NoSuchClassInContribError: 찾으려는 클래스가 존재하지 않을 때 발생
        """

        _type = _type.lower()
        _name = _name.lower()
        module = self._ext_.get_class("model",_name)

        if module is None:
            raise error.NoSuchClassInContribError()

        if _type == "model":
            return module.Model
        elif _type == "dataset":
            return module.Dataset
        elif _type == "config":
            return module.Config
        return None

    def obj_type(self, obj_name:str, *args):
        """Contrib나 기본지원되는 타입의 객체를 생성합니다.

        Args:
            obj_name: 타입을 식별할 수 있는 고유 id 값입니다.
            args: 타입의 인자값을 넣습니다.

        Returns:
            요청한 이름의 객체를 반환합니다.
            obj_name에 벗어난 데이터는 None을 반환합니다.

        Raises:
            NoSuchClassInContribError: 찾으려는 클래스가 존재하지 않을 때 발생
        """

        cs = self.class_type(obj_name)
        return cs.obj(args)

    def class_type(self, obj_name:str):
        """Contrib나 기본지원되는 타입을 반환합니다.

        Args:
            obj_name: 타입을 식별할 수 있는 고유 id 값입니다.

        Returns:
            요청한 이름의 클래스를 반환합니다.
            obj_name에 벗어난 데이터는 None을 반환합니다.

        Raises:
            NoSuchClassInContribError: 찾으려는 클래스가 존재하지 않을 때 발생
        """
        
        cs = self._ext_.get_class("type",obj_name)
        if cs is None:
            raise error.NoSuchClassInContribError()
        return cs

    def locator(self, name, data):
        """

        Args:

        Returns:

        Raises:
           
        """

        print("준비중")

    def get_model_list(self) -> list:
        """등록된 모델의 정보를 반환합니다.

        Returns:
            등록된 모델의 정보를 반환합니다.
            list 형태로 반환합니다.
        """

        return list(self._model_.keys())

    def add_model(self, model_name:str, lib_name:str, config_data) -> None:
        """학습 모델을 추가합니다.

        Args:
            model_name: 식별 id입니다.
            lib_name: model 라이브러리 이름입니다.
            config_data: model 라이브러리에 사용될 config 데이터입니다. 
                         config는 각 모델 라이브러리에서 지원하는 형태에 
                         따라 다릅니다.
                         권장형태는 dict, uri(str) 입니다.

        Raises:
           NoSuchClassInContribError: 찾으려는 클래스가 존재하지 않을 때 발생
        """

        c_config = self._get_model_class(lib_name, "config")
        c_model = self._get_model_class(lib_name, "model")
        if c_config is None or c_model is None:
            raise error.NoSuchClassInContribError()

        config = c_config()
        config.load_config(config_data)
        model = c_model(config)

        self._model_.update({model_name:model})        
    
    def set_model_config(self,model_name:str, data:dict) -> None:
        """모델 config의 값을 수정합니다.

        Args:
            model_name: 수정하려는 모델의 키 값을 입력합니다.
            data: 수정하려는 정보를 key:value 형태로 입력합니다.
        """

        model = self._get_model(model_name)
        for key in list(data.keys()):
            model.get_config().set_config(key,data[key])

    def get_model_config(self, model_name:str, key:str) -> object:
        """모델 config의 특정 key의 정보를 가져옵니다.

        Args:
            model_name: 가져오려는 모델의 키 값을 입력합니다.
            key: config에서 원하는 데이터의 키 값을 입력합니다.

        Returns:
            config의 특정 값을 반환합니다. 
            권장하는 반환 형태는 str 이지만 실제로는 Numpy 데이터, list, dict일 수 있습니다.
        """

        model = self._get_model(model_name)
        return model.get_config().get_value(key)

    def delete_model(self, name:str) -> None:
        """등록된 모델을 해제 합니다.

        Args:
            name: 삭제하려는 모델의 키 값을 입력합니다.

        Raises:
           NoSuchClassInContribError: 찾으려는 클래스가 존재하지 않을 때 발생
        """

        if not name in self._model_:
            raise error.NoSuchClassInContribError()

        del self._model_[name]
        
    def add_model_dataset(self, model_name:str, dataset_name:str, lib_name:str) -> None:
        """모델에 데이터셋을 등록합니다.

        Args:
            model_name: 등록하려는 모델을 입력합니다.
            dataset_name: 등록하려는 데이터셋 id(key)값을 입력합니다.
            lib_name: 등력하려는 데이터셋의 라이브러리 이름을 입력합니다.
        """

        model = self._get_model(model_name)
        dataset = self._get_model_class(lib_name,"dataset")()
        dataset.set_config(model.get_config())
        model.add_dataset(dataset_name, dataset)

    def delete_model_dataset(self, model_name:str, dataset_name:str) -> None:
        """모델에 등록된 데이터셋을 삭제합니다.

        Args:
            model_name: 삭제하려는 데이터셋의 모델의 key 값을 입력합니다.
            dataset_name: 삭제하려는 데이터셋의 key 값을 입력합니다.
        """

        model =self._get_model(model_name)
        model.delete_dataset(dataset_name)

    def add_data(self, model_name:str, dataset_name:str, data) -> None:
        """데이터셋에 데이터를 입력합니다.

        Args:
            model_name: 데이터를 등록하려는 데이터셋이 소속된 모델의 key 값
            dataset_name: 데이터를 등록하려는 데이터셋의 key 값
            data: 등록하려는 데이터
       
        """

        model = self._get_model_(model_name)
        model.add_data(dataset_name, data)

    def train(self, model_name:str, train_dataset_name:str, validation_dataset_name:str, weight) -> object:
        """학습을 합니다.

        Args:
            name: 학습하려는 모델을 선택합니다.
            train_dataset_name: 학습하려는 데이터셋의 이름을 입력합니다.
            validation_dataset_name: 검증하려는 데이터셋의 이름을 입력합니다.
            weight: last, None, path+model_name
                    None : config 파일에 입력된 정보로 처리합니다.
        Returns:
            학습 정보가 업데이트 된 config를 반환합니다.
        Raises:
            KeyNotNoneError: 존재하지 않은 데이터셋을 사용했습니다.
        """

        model = self._get_model(model_name)
        if model.get_dataset(train_dataset_name) is None or model.get_dataset(validation_dataset_name) is None:
            raise KeyNotNoneError()
        model.train(train_dataset_name, validation_dataset_name, weight)
        return model.get_config()
    
    def detect(self, model_name:str, row_data, option=1) -> list:
        """예측합니다.

        Args:
            model_name: 사용할 모델을 선택합니다.
            row_data: 예측에 사용할 데이터입니다.
            option: 각 모델 별로 지원하는 옵션 값입니다.
        Returns:
            입력한 형태로 이루어진 배열로 반환합니다.
            (배열이라면 배열로 반환)
        """

        result= []
        model = self._get_model(model_name)
        if not isinstance(row_data,list):
            row_data = [row_data]
        for data in row_data:
            result.append(model.detect(data,option))
        return result
    





if __name__ == "__main__":
    engine = Engine()
    # engine.add_model('mscoco','Yolo','D:/Project/tmp/yolo.config.json')
    engine.add_model('mscoco','maskrcnn','D:/Project/tmp/maskrcnn_config.json')

    image=engine.obj_type("stphoto","image.jpg","D:/Project/")
    print(image)
    engine.detect('mscoco',image)

    print(image.to_stphoto())