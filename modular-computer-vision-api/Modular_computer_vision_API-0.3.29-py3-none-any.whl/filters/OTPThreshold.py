from OTPBase import OTPBase
import cv2

class OTPThreshold(OTPBase):
    """
    Applies cv2.threshold to an image.
    Return: Segmented image
    Sets variables:
        - _in_original_image: original image before threshold
        - _out_segmented_image: image after threshold
    """

    def __init__(self, **kwargs):
        super(OTPThreshold, self).__init__(**kwargs)
       
        self._param_threshold_type = cv2.THRESH_BINARY
        self._param_threshold_maxval = 255
        self._param_threshold_thresh = 130

    def compute(self, frame):
        _, img = cv2.threshold(frame, 
            self._param_threshold_thresh,
            self._param_threshold_maxval, 
            self._param_threshold_type)
        return img

    def process(self, image):
        self._in_original_image = image
        value = super(OTPThreshold, self).process(image)
        self._out_segmented_image = OTPThreshold.compute(self,value)
        return self._out_segmented_image