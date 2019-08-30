import numpy as np
from tools import *
from OTPBase import OTPBase
import math


class OTPOrderExtremePointsPerAngle(OTPBase):
    """
    Order the blobs by position
    Return: Ordered blobs
    """

    def __init__(self, **kwargs): 
        super(OTPOrderExtremePointsPerAngle, self).__init__(**kwargs)
        self._orderextrempoints_last_blobs = []

    def compute(self, blobs):
    
        if  len( blobs )>1 and \
            len( blobs )==len(self._orderextrempoints_last_blobs):
            #Only one blob
            #The same number of blobs from the last frame
            
            for b1, b2 in zip(blobs,self._orderextrempoints_last_blobs):
                b1_angle = points_angle( b1._head, b1._tail)
                b2_angle = points_angle( b2._head, b2._tail)
                angle_diff = min_dist_angles(b1_angle, b2_angle)

                if angle_diff>(np.pi/2): b1.flip()
                
        self._orderextrempoints_last_blobs = blobs
        return blobs

    def process(self, blobs):
        blobs = super(OTPOrderExtremePointsPerAngle, self).process(blobs)
        return OTPOrderExtremePointsPerAngle.compute(self, blobs)
