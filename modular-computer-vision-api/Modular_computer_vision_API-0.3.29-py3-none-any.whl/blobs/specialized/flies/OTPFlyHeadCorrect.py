import numpy as np, math
from tools import *
from OTPBase import OTPBase



class OTPFlyHeadCorrect(OTPBase):

    def __init__(self, **kwargs):
        super(OTPFlyHeadCorrect, self).__init__(**kwargs)


    def compute(self, blobs):      
        for blob in blobs:
            center,axes,angle_degrees = cv2.fitEllipse(blob._contour)

            angle = math.radians(angle_degrees-90)
            head = int(round(math.cos(angle)*axes[1]/2 + center[0])), int(round(math.sin(angle)*axes[1]/2 + center[1]))
            
            if lin_dist(head, blob._tail) < lin_dist(head, center):
                angle = math.radians(angle_degrees+90)
                head = int(round(math.cos(angle)*axes[1]/2 + center[0])), int(round(math.sin(angle)*axes[1]/2 + center[1]))
                
            blob._head = head
            
        return blobs

    def process(self, blobs):
        blobs = super(OTPFlyHeadCorrect, self).process(blobs)
        return OTPFlyHeadCorrect.compute(self, blobs)