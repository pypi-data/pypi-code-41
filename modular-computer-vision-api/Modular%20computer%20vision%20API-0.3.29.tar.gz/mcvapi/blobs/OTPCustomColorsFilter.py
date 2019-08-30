from OTPBase import OTPBase
import cv2

class OTPCustomColorsFilter(OTPBase):
    """
    Applies cv2.threshold to an image.
    Return: Segmented image
    Sets variables:
        - _in_original_image: original image before threshold
        - _out_segmented_image: image after threshold
    """

    def __init__(self, **kwargs):
        super(OTPCustomColorsFilter, self).__init__(**kwargs)
       
        self._param_threshold_type = cv2.THRESH_BINARY
        self._param_threshold_maxval = 255
        self._param_threshold_thresh = 130

    def compute(self, frame):
        #_,thresh = cv2.threshold(frame,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #blur_thresh = cv2.blur( thresh, (11,11) )
        _, img = cv2.threshold(frame, 200,255, cv2.THRESH_BINARY_INV)

        #cv2.imshow("mas", img)
        return img

    def process(self, image):
        self._in_original_image = image
        value = super(OTPCustomColorsFilter, self).process(image)
        self._out_segmented_image = OTPCustomColorsFilter.compute(self,value)
        return self._out_segmented_image