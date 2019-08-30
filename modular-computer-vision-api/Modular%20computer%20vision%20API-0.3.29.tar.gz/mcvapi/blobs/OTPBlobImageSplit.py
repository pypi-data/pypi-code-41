import numpy as np
from OTPAdaptativeThreshold import OTPAdaptativeThreshold
from OTPBlur import OTPBlur
from OTPMaskImage import OTPMaskImage
from OTPFindBlobs import OTPFindBlobs
from OTPSelectBiggerBlobs import OTPSelectBiggerBlobs

class ImageSegmentation(OTPBlur,OTPAdaptativeThreshold):

    def __init__(self, **kwargs):
        super(ImageSegmentation, self).__init__(**kwargs)

        self._param_tb_color_component = 2 
        self._param_tb_color_domain = 40 
        self._param_tb_adaptive_method = 1 
        self._param_tb_block_size = 500 
        self._param_tb_c = 259 
        self._param_kernel_size = 5 
        self._param_blur_threshould = 189

    def compute(self, frame):
        return frame

    def process(self, image):
        image = super(ImageSegmentation, self).process(image)
        self._out_image_segmentation = image
        return ImageSegmentation.compute(self,image)


if __name__ == "__main__":
    import cv2
    capture = cv2.VideoCapture("/home/ricardo/Desktop/led30.avi")
    module = ImageSegmentation()

    while True:
        res, frame = capture.read()
        if not res: break;

        frame = module.process(frame)
        cv2.imshow("Capture", frame)

        key = cv2.waitKey(1)
        if key == ord('q'): break