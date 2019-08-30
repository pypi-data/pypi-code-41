import cv2, time, itertools
from numpy import *
from math import *

from OTPBase import *


class OTPSelectBySizeRatio(OTPBase):
    """
    Selects the biggest blobs
    Return: Return the number of blobs setted in the variable _param_n_blobs
    """

    def __init__(self, **kwargs):
    	super(OTPSelectBySizeRatio, self).__init__(**kwargs)
        
        self._param_size_ratio_max = 0.8
        self._param_size_ratio_min = 0.3
        self._param_size_ratio_max_height = 60
        self._param_size_ratio_max_width = 30

    def compute(self, blobs):
        res = []
        for blob in blobs:
            ratio = blob._area / (blob._ellipse_axis[0]*blob._ellipse_axis[1])
            if self._param_size_ratio_min<=ratio<=self._param_size_ratio_max and \
                blob._ellipse_axis[0]<=self._param_size_ratio_max_width and \
                blob._ellipse_axis[1]<=self._param_size_ratio_max_height:
                #print blob._ellipse_axis
                res.append(blob)
        return res
        

    def process(self, blobs):
    	blobs = super(OTPSelectBySizeRatio, self).process(blobs)
        return OTPSelectBySizeRatio.compute(self,blobs)