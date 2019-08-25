from deepgeo.image import obj as Image
from deepgeo.util import create, polygon

from .Config import Config
import numpy as np
import cv2


class Model:
    class ModelError(Exception):
        """Exception raised for errors in the input.
        Attributes:
            expression -- input expression in which the error occurred
            message -- explanation of the error
        """
        pass
    
    def __init__(self, config:Config):
        assert config is not None, "__init__ : config is None"
        self._config_ = config
        self._model_path_ = create.folder(self._config_.MODEL_PATH.split(self._config_.MODEL_FILE_NAME)[0])
                  #    NET      VERSION   LAYER
        self._model_ = [None, "inference", None]
    
    def __get_output_layers(self):
        layer_names = self._model_[0].getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self._model_[0].getUnconnectedOutLayers()]
        return output_layers

    def _get_model_(self, name, mode):
        if self._model_[0] is not None and self._model_[1] == mode:
            return self._model_[0]
        if mode == "training":
            self._config_.set_config("IMAGES_PER_GPU",1)
        model = cv2.dnn.readNet(self._model_path_+self._config_.MODEL_FILE_NAME, self._model_path_+self._config_.CONFIG)
        
        self._model_[0] = model
        self._model_[1] = mode
        self._model_[2] = self.__get_output_layers()
        return self._model_

    def _to_format_(self, data, boxes,confidence,class_ids):
        if isinstance(data, Image):
            annotations = []
            for idx in range(len(class_ids)):
                try:
                    annotation ={
                        "areaInImage":{
                            "type": "bbox",
                            "coordinates":boxes[idx],
                            "score":float(confidence[idx])
                        },
                        "annotationText":self._config_.CATEGORY[class_ids[idx]]
                    }
                    annotations.append(annotation)
                except Exception as e:
                    print(idx, " - pass! - ", e)
            data.add_annotation(annotations)
            return data
        else:
            return boxes,confidence,class_ids

    def detect(self, data, option):
        b_data = data
        if isinstance(data, Image):
            b_data = data.to_numpy()
        scale =  0.00392
        width = b_data.shape[1]
        height = b_data.shape[0]
        if height > width:
            width ^= height
            height ^= width
            width ^= height

        model_path  = create.folder(self._config_.MODEL_PATH)
        model = self._get_model_(model_path+self._config_.MODEL_FILE_NAME,"inference")
        try:
            blob = cv2.dnn.blobFromImage(b_data, scale, (416,416), (0,0,0), True, crop=False)
            model[0].setInput(blob)
            outs = model[0].forward(model[2])
            class_ids = []
            confidences = []
            boxes = []
            conf_threshold = 0.5
            nms_threshold = 0.4
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        class_ids.append(class_id)
                        confidences.append(float(confidence))
                        boxes.append([x, y, w, h])
            # indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
            # print(boxes,confidences,class_ids)
            return self._to_format_(data, boxes,confidences,class_ids)
        except Exception as e:
            print(str(e))
        
        return data

    def create_dataset(self, name):
        pass

    def add_dataset(self, name, dataset):
        pass

    def delete_dataset(self, name):
        pass

    def add_data(self, name, data):
        pass

    def validation(self, validation_dataset_name, weight:str=None):
        pass

    def train(self, train_dataset_name, validation_dataset_name, weight:str=None):
        pass