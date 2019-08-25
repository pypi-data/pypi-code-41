"""
Mask R-CNN
Base Configurations class.

Copyright (c) 2017 Matterport, Inc.
Licensed under the MIT License (see LICENSE for details)
Written by Waleed Abdulla

Copyright (c) 2019 KSUN InfoLab.
Licensed under the MIT License (see LICENSE for details)
Written by Donggun LEE

"""

import numpy as np
import json

# Base Configuration Class
# Don't use this class directly. Instead, sub-class it and override
# the configurations you need to change.

class Config:
    def __init__(self):
        self.CATEGORY = ['BG']
        self.IMAGE_PATH = ""
        self.MODEL_FILE_NAME = ""
        self.MODEL_PATH = ""
        self.VERSION = ""
        self.MEMO = ""
        self.EPOCHS=1
        self.LAYERS="all"
        self.RESULT_TEST_NUM=100

        # Name the configurations. For example, 'COCO', 'Experiment 3', ...etc.
        # Useful if your code needs to do things differently depending on which
        # experiment is running.
        self.NAME = None  # Override in sub-classes

        # NUMBER OF GPUs to use. When using only a CPU, this needs to be set to 1.
        self.GPU_COUNT = 1

        # Number of images to train with on each GPU. A 12GB GPU can typically
        # handle 2 images of 1024x1024px.
        # Adjust based on your GPU memory and image sizes. Use the highest
        # number that your GPU can handle for best performance.
        self.IMAGES_PER_GPU = 2

        # Number of training steps per epoch
        # This doesn't need to match the size of the training set. Tensorboard
        # updates are saved at the end of each epoch, so setting this to a
        # smaller number means getting more frequent TensorBoard updates.
        # Validation stats are also calculated at each epoch end and they
        # might take a while, so don't set this too small to avoid spending
        # a lot of time on validation stats.
        self.STEPS_PER_EPOCH = 1000

        # Number of validation steps to run at the end of every training epoch.
        # A bigger number improves accuracy of validation stats, but slows
        # down the training.
        self.VALIDATION_STEPS = 50

        # Backbone network architecture
        # Supported values are: resnet50, resnet101.
        # You can also provide a callable that should have the signature
        # of model.resnet_graph. If you do so, you need to supply a callable
        # to COMPUTE_BACKBONE_SHAPE as well
        self.BACKBONE = "resnet101"

        # Only useful if you supply a callable to BACKBONE. Should compute
        # the shape of each layer of the FPN Pyramid.
        # See model.compute_backbone_shapes
        self.COMPUTE_BACKBONE_SHAPE = None

        # The strides of each layer of the FPN Pyramid. These values
        # are based on a Resnet101 backbone.
        self.BACKBONE_STRIDES = [4, 8, 16, 32, 64]

        # Size of the fully-connected layers in the classification graph
        self.FPN_CLASSIF_FC_LAYERS_SIZE = 1024

        # Size of the top-down layers used to build the feature pyramid
        self.TOP_DOWN_PYRAMID_SIZE = 256

        # Number of classification classes (including background)
        self.NUM_CLASSES = 1  # Override in sub-classes

        # Length of square anchor side in pixels
        self.RPN_ANCHOR_SCALES = (32, 64, 128, 256, 512)

        # Ratios of anchors at each cell (width/height)
        # A value of 1 represents a square anchor, and 0.5 is a wide anchor
        self.RPN_ANCHOR_RATIOS = [0.5, 1, 2]

        # Anchor stride
        # If 1 then anchors are created for each cell in the backbone feature map.
        # If 2, then anchors are created for every other cell, and so on.
        self.RPN_ANCHOR_STRIDE = 1

        # Non-max suppression threshold to filter RPN proposals.
        # You can increase this during training to generate more propsals.
        self.RPN_NMS_THRESHOLD = 0.7

        # How many anchors per image to use for RPN training
        self.RPN_TRAIN_ANCHORS_PER_IMAGE = 256
        
        # ROIs kept after tf.nn.top_k and before non-maximum suppression
        self.PRE_NMS_LIMIT = 6000

        # ROIs kept after non-maximum suppression (training and inference)
        self.POST_NMS_ROIS_TRAINING = 2000
        self.POST_NMS_ROIS_INFERENCE = 1000

        # If enabled, resizes instance masks to a smaller size to reduce
        # memory load. Recommended when using high-resolution images.
        self.USE_MINI_MASK = True
        self.MINI_MASK_SHAPE = (56, 56)  # (height, width) of the mini-mask

        # Input image resizing
        # Generally, use the "square" resizing mode for training and predicting
        # and it should work well in most cases. In this mode, images are scaled
        # up such that the small side is = IMAGE_MIN_DIM, but ensuring that the
        # scaling doesn't make the long side > IMAGE_MAX_DIM. Then the image is
        # padded with zeros to make it a square so multiple images can be put
        # in one batch.
        # Available resizing modes:
        # none:   No resizing or padding. Return the image unchanged.
        # square: Resize and pad with zeros to get a square image
        #         of size [max_dim, max_dim].
        # pad64:  Pads width and height with zeros to make them multiples of 64.
        #         If IMAGE_MIN_DIM or IMAGE_MIN_SCALE are not None, then it scales
        #         up before padding. IMAGE_MAX_DIM is ignored in this mode.
        #         The multiple of 64 is needed to ensure smooth scaling of feature
        #         maps up and down the 6 levels of the FPN pyramid (2**6=64).
        # crop:   Picks random crops from the image. First, scales the image based
        #         on IMAGE_MIN_DIM and IMAGE_MIN_SCALE, then picks a random crop of
        #         size IMAGE_MIN_DIM x IMAGE_MIN_DIM. Can be used in training only.
        #         IMAGE_MAX_DIM is not used in this mode.
        self.IMAGE_RESIZE_MODE = "square"
        self.IMAGE_MIN_DIM = 800
        self.IMAGE_MAX_DIM = 1024
        # Minimum scaling ratio. Checked after MIN_IMAGE_DIM and can force further
        # up scaling. For example, if set to 2 then images are scaled up to double
        # the width and height, or more, even if MIN_IMAGE_DIM doesn't require it.
        # However, in 'square' mode, it can be overruled by IMAGE_MAX_DIM.
        self.IMAGE_MIN_SCALE = 0
        # Number of color channels per image. RGB = 3, grayscale = 1, RGB-D = 4
        # Changing this requires other changes in the code. See the WIKI for more
        # details: https://github.com/matterport/Mask_RCNN/wiki
        self.IMAGE_CHANNEL_COUNT = 3

        # Image mean (RGB)
        self.MEAN_PIXEL = np.array([123.7, 116.8, 103.9])

        # Number of ROIs per image to feed to classifier/mask heads
        # The Mask RCNN paper uses 512 but often the RPN doesn't generate
        # enough positive proposals to fill this and keep a positive:negative
        # ratio of 1:3. You can increase the number of proposals by adjusting
        # the RPN NMS threshold.
        self.TRAIN_ROIS_PER_IMAGE = 200

        # Percent of positive ROIs used to train classifier/mask heads
        self.ROI_POSITIVE_RATIO = 0.33

        # Pooled ROIs
        self.POOL_SIZE = 7
        self.MASK_POOL_SIZE = 14

        # Shape of output mask
        # To change this you also need to change the neural network mask branch
        self.MASK_SHAPE = [28, 28]

        # Maximum number of ground truth instances to use in one image
        self.MAX_GT_INSTANCES = 100

        # Bounding box refinement standard deviation for RPN and final detections.
        self.RPN_BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])
        self.BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])

        # Max number of final detections
        self.DETECTION_MAX_INSTANCES = 100

        # Minimum probability value to accept a detected instance
        # ROIs below this threshold are skipped
        self.DETECTION_MIN_CONFIDENCE = 0.7

        # Non-maximum suppression threshold for detection
        self.DETECTION_NMS_THRESHOLD = 0.3

        # Learning rate and momentum
        # The Mask RCNN paper uses lr=0.02, but on TensorFlow it causes
        # weights to explode. Likely due to differences in optimizer
        # implementation.
        self.LEARNING_RATE = 0.001
        self.LEARNING_MOMENTUM = 0.9

        # Weight decay regularization
        self.WEIGHT_DECAY = 0.0001

        # Loss weights for more precise optimization.
        # Can be used for R-CNN training setup.
        self.LOSS_WEIGHTS = {
            "rpn_class_loss": 1.,
            "rpn_bbox_loss": 1.,
            "mrcnn_class_loss": 1.,
            "mrcnn_bbox_loss": 1.,
            "mrcnn_mask_loss": 1.
        }

        # Use RPN ROIs or externally generated ROIs for training
        # Keep this True for most situations. Set to False if you want to train
        # the head branches on ROI generated by code rather than the ROIs from
        # the RPN. For example, to debug the classifier head without having to
        # train the RPN.
        self.USE_RPN_ROIS = True

        # Train or freeze batch normalization layers
        #     None: Train BN layers. This is the normal mode
        #     False: Freeze BN layers. Good when using a small batch size
        #     True: (don't use). Set layer in training mode even when predicting
        self.TRAIN_BN = False  # Defaulting to False since batch size is often small

        # Gradient norm clipping
        self.GRADIENT_CLIP_NORM = 5.0

        self._setting_()

    def _setting_(self):
        """Set values of computed attributes."""
        # Effective batch size
        self.BATCH_SIZE = self.IMAGES_PER_GPU * self.GPU_COUNT

        # Input image size
        if self.IMAGE_RESIZE_MODE == "crop":
            self.IMAGE_SHAPE = np.array([self.IMAGE_MIN_DIM, self.IMAGE_MIN_DIM,
                self.IMAGE_CHANNEL_COUNT])
        else:
            self.IMAGE_SHAPE = np.array([self.IMAGE_MAX_DIM, self.IMAGE_MAX_DIM,
                self.IMAGE_CHANNEL_COUNT])

        # Image meta data length
        # See compose_image_meta() for details
        self.IMAGE_META_SIZE = 1 + 3 + 3 + 4 + 1 + self.NUM_CLASSES

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
        self.NUM_CLASSES = len(self.CATEGORY)
        self.RPN_ANCHOR_SCALES=tuple(self.RPN_ANCHOR_SCALES)
        self.MINI_MASK_SHAPE=tuple(self.MINI_MASK_SHAPE)
        self.MEAN_PIXEL=np.array(self.MEAN_PIXEL)
        self._setting_()
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
            self._setting_()

    def save_config(self, path:str, file_name:str):
        """
            # save_config : 설정 데이터를 json 파일 형태로 저장합니다.

            path : 저장할 경로를 입력합니다. 
            -------------------------------------
            file_name : 저장할 파일 명을 입력합니다. 
        """
        assert path is not None or path != "", "save_config : path is None"
        assert file_name is not None or file_name != "", "save_config : file_name is None"

        path = utils.create_folder(path)
        file_name = file_name.replace("."+file_name.split(".")[-1],"")
        path = path + file_name + ".json"
        data = self._to_json_()
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent='\t', sort_keys=True, default=utils.default_DICT_TO_JSON)
        del file_name
        del data
        return path

    def display(self):
        print(self._to_json_())