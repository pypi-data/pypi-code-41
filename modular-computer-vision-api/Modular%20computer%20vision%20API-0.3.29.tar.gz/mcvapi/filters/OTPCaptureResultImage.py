import numpy as np
from tools import *
from OTPBase import OTPBase



class OTPCaptureResultImage(OTPBase):

    def __init__(self, **kwargs): super(OTPCaptureResultImage, self).__init__(**kwargs)

    def process(self, image):
        res = super(OTPCaptureResultImage, self).process(image)
        self._captured_result_image = res
        return res













