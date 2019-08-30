from OTPBase import OTPBase
import numpy as np
import cv2

class OTPNoiseRemover(OTPBase):
    """
    Applies cv2.threshold to an image.
    Return: Binary segmented image
    """

    def __init__(self, **kwargs):
        super(OTPNoiseRemover, self).__init__(**kwargs)

        self._param_threshold_type = cv2.THRESH_BINARY
        self._param_threshold_maxval = 255
        self._param_threshold_thresh = 130

    def compute(self, frame):
        # kernel = np.ones((3, 3),np.uint8)
        kernel= cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        img = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
        return img

    def process(self, image):
        self._in_original_image = image
        value = super(OTPNoiseRemover, self).process(image)

        #Convert image to Gray
        if len(value.shape)>2:  value = cv2.cvtColor(value, cv2.cv.CV_RGB2GRAY)
        return OTPNoiseRemover.compute(self,value)
