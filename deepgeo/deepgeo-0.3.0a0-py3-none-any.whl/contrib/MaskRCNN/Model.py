from deepgeo.util import create, polygon
from deepgeo.image import obj as Image
from . import Lib
from . import Utils
from . import Config
from . import Dataset

import numpy as np

class Model:
    FIRST_POLYGON_DATA = 1
    FIRST_BBOX_DATA = 2
    FIRST_BBOX_DATA_WITH_SAVE = 3
    FIRST_POLYGON_DATA_WITH_SAVE = 4
    _OPTION_ = [FIRST_POLYGON_DATA,FIRST_BBOX_DATA,FIRST_BBOX_DATA_WITH_SAVE,FIRST_POLYGON_DATA_WITH_SAVE]
    def __init__(self, config:Config):
        """
            # __init__ : Model를 생성하고 설정파일로 설정합니다.

            config : Config 타입만 받습니다.
        """
        assert config is not None, "__init__ : config is None"
        self._config_ = config
        self._dataset_={}
        self._model_path_ = create.folder(self._config_.MODEL_PATH.split(self._config_.MODEL_FILE_NAME)[0])
        self._model_ = [None, "training"]
    
    def _get_model_(self, name, mode):
        """
            # _get_model_ : 모델 데이터를 메모리에 올립니다.

            name : 모델 데이터의 위치와 파일명이 들어 있는 경로, 혹은 last , None 데이터를 받습니다.
            if name is "last" : 마지막으로 학습된 데이터를 가져옵니다.
            if name is None : 기본 모델 데이터를 가져옵니다.
            if name is path : 해당 파일을 읽어옵니다.
            -------------------------------------
            mode : 학습인지 분석인지 선택합니다.
            if mode is "inference" : 분석 모드로 모델을 설정합니다.
            if mode is "training" : 학습 모드로 모델을 설정합니다.
        """
        if self._model_[0] is not None and self._model_[1] == mode:
            return self._model_[0]
        if mode == "training":
            self._config_.set_config("IMAGES_PER_GPU",1)
        model = Lib.MaskRCNN(mode=mode, config=self._config_, model_dir=self._model_path_)
        if name is None:
            name = model.get_imagenet_weights()
        elif name == "last":
            name = model.find_last()[1]
        assert name != "", "Provide path to trained weights"
        print("Loading weights from ", name)
        model.load_weights(name, by_name =True)
        self._model_[0] = model
        self._model_[1] = mode
        return self._model_[0]

    def get_config(self):
        """
            # get_config : 설정 데이터를 반환합니다.
        """
        return self._config_

    def create_dataset(self, name):
        """
            # create_dataset : 데이터셋을 생성합니다.
            
            name : 생성할 데이터셋의 이름을 지정합니다. 중복시 이전 것은 제거 됩니다.
        """
        dataset = Dataset()
        dataset.set_config(self._config_)
        self._dataset_.update({name:dataset})

    def get_dataset(self, name):
        """
            # get_dataset : 데이터셋을 가져옵니다.

            name : 데이터셋의 이름입니다.
        """
        if name in list(self._dataset_.keys()):
            return self._dataset_[name]
        return None

    def add_dataset(self, name, dataset:Dataset):
        """
            # add_dataset : 외부 데이터 셋을 추가합니다.

            name : 데이터셋의 이름을 지정합니다. 중복시 이전 것은 제거 됩니다.
            -------------------------------------
            dataset : Dataset 타입의 객체만 받습니다.
        """
        self._dataset_.update({name:dataset})

    def delete_dataset(self, name):
        del self._dataset_[name]

    def add_data(self, name, data):
        """
            # add_data : 학습할 데이터를 추가합니다.

            name : 추가할 데이터셋 이름을 입력합니다.
            -------------------------------------
            data : 데이터를 추가합니다.
        """
        self._dataset_[name].add_data(data)

    def validation(self, validation_dataset_name, weight:str):
        """
            # validation : 검증을 진행합니다.

            validation_dataset_name : 검증으로 사용할 데이터셋의 이름을 입력합니다.
            -------------------------------------
            weight : 사용할 가중치 정보를 입력합니다. (last, None, path+model_name)
        """
        model = self._get_model_(weight,"inference")
        dataset_val = self._dataset_[validation_dataset_name]
        dataset_val.prepare()

        image_ids = np.random.choice(dataset_val.image_ids, self._config_.RESULT_TEST_NUM)
        APs = []
        for image_id in image_ids:
            # Load image and ground truth data
            image, _, gt_bbox, _ = \
                Lib.load_image_gt(dataset_val, self._config_,
                                    image_id, use_mini_mask=True)
            _ = np.expand_dims(Lib.mold_image(image, self._config_), 0)
            # Run object detection
            results = model.detect([image], verbose=0)
            r = results[0]
            # Compute AP
            AP, _, _, _ = \
                Utils.compute_ap(gt_bbox[:, :4], gt_bbox[:, 4],
                                r["rois"], r["class_ids"], r["scores"])
            APs.append(AP)
        print("mAP: ", np.mean(APs))

    def train(self, train_dataset_name, validation_dataset_name, weight:str=None):
        """
            # train : 학습을 진행합니다.

            train_dataset_name : 학습할 데이터셋의 이름을 입력합니다.
            -------------------------------------
            validation_dataset_name : 검증으로 사용할 데이터셋의 이름을 입력합니다.
            -------------------------------------
            weight : 사용할 가중치 정보를 입력합니다. (last, None, path+model_name)
        """
        model = self._get_model_(weight,"training")

         # 학습할 데이터 셋
        dataset_train = self._dataset_[train_dataset_name]
        dataset_train.prepare()

        # 점검할 데이터 셋
        dataset_val = self._dataset_[validation_dataset_name]
        dataset_val.prepare()
        
        print("학습 시작")
        model.train(dataset_train, dataset_val,learning_rate=self._config_.LEARNING_RATE,
                        epochs=self._config_.EPOCHS,layers=self._config_.LAYERS)

        print("학습 완료")
        model_path = model.find_last()[1]
        del model
        del dataset_train
        del dataset_val
        model_path = model_path.replace("\\","/")
        self._config_.MODEL_FILE_NAME = model_path.split("/")[-1]
        self._config_.MODEL_PATH = model_path.split(self._config_.MODEL_FILE_NAME)[0]
        return model_path

    def detect(self, data, option=1):
        """
            # detect : 데이터 분석을 진행합니다.
            
            data : 분석할 데이터를 받습니다. Image 및 ndarray 만 받습니다.
            -------------------------------------
            option : 예측할 때 조건을 제시합니다.
                FIRST_BBOX_DATA_WITH_SAVE : BBOX를 우선으로 저장을 합니다.
                FIRST_POLYGON_DATA_WITH_SAVE : POLYGON를 우선으로 저장합니다.
        """
        assert isinstance(data, Image) or isinstance(data, np.ndarray), "Model -> detect -> 지원하지 않은 포맷입니다. (: " + str(type(data)) +" :)"
        assert option in Model._OPTION_  or option is None, "Model -> detect -> 지원하지 않은 옵션입니다."

        model_path  = create.folder(self._config_.MODEL_PATH)
        model = self._get_model_(model_path+self._config_.MODEL_FILE_NAME,"inference")

        if isinstance(data, Image):
            numpy_array = [data.to_numpy()]
        else:
            numpy_array = [data]

        result = model.detect(numpy_array, verbose=0)

        if isinstance(data, np.ndarray):
            return result

        points = None

        issave = False
        if option in [Model.FIRST_BBOX_DATA_WITH_SAVE, Model.FIRST_POLYGON_DATA_WITH_SAVE]:
            issave=True
        img = result[0]
        annotations = []
        
        if option == Model.FIRST_BBOX_DATA:
            points = img['rois'].tolist()
            option = "bbox"
        else:
            points = polygon.from_numpy(img["masks"])
            option = "polygon"
            
        cnt_ids = len(img['class_ids'])
        for idx in range(cnt_ids):
            try:
                annotation ={
                    "areaInImage":{
                        "type": option,
                        "coordinates":points[idx],
                        "score":float(img['scores'][idx])
                    },
                    "annotationText":self._config_.CATEGORY[img['class_ids'][idx]]
                }
                annotations.append(annotation)
            except Exception as e:
                print(idx, " - pass! - ", e)
        data.add_annotation(annotations)
        if issave is True:
            info = data.to_stphoto()
            data.draw_annotations(info['annotations'],option="PolygonAndRectangleTextWithBackground")
            data.save(self._config_.IMAGE_PATH, image_name=None, image_format="png")
        del model_path
        del numpy_array
        del points
        del issave
        del annotations
        return data