import numpy as np
from tools import *
from OTPBase import OTPBase
from intelligence.VirtualModel import VirtualModel
from intelligence.VirtualFly import VirtualFly

class OTPFliesPostureEstimator(OTPBase):

    def __init__(self, **kwargs):
        super(OTPFliesPostureEstimator, self).__init__(**kwargs)
        self._model = VirtualModel()

    def __correct_head_tail(self, blobs):
        for blob in blobs:
            center,axes,angle_degrees = cv2.fitEllipse(blob._contour)
            angle = math.radians(angle_degrees-90)
            head = int(round(math.cos(angle)*axes[1]/2 + center[0])), int(round(math.sin(angle)*axes[1]/2 + center[1]))
            if lin_dist(head, blob._tail) < lin_dist(head, center):
                angle = math.radians(angle_degrees+90)
                head = int(round(math.cos(angle)*axes[1]/2 + center[0])), int(round(math.sin(angle)*axes[1]/2 + center[1]))
            blob._head = head
            center = int(round(center[0])), int(round(center[1]))
            blob._centroid = center
        return blobs



    def compute(self, blobs):        
        #Flies aren't merged
        if self._flies_bodies_split==0:
            blobs = self.__correct_head_tail(blobs)
            for blob in blobs:
                fly = VirtualFly( blob.positionInImage )
                fit, virtualflies = self._model.fitflies( blob._body_image, blob._wings_image, [fly])
                virtualflies[0].draw(blob._image)
                min_angle = abs(minimumAngleBetween(blob.angle_degrees, virtualflies[0].angleTailHead))
                if min_angle>90: blob.flip()

        #Flies are merged but bodies not
        elif self._flies_bodies_split==1:
            blobs = self.__correct_head_tail(blobs)

            virtualflies = []
            for blob in blobs:
                fly = VirtualFly( blob.positionInImage )
                virtualflies.append( fly )

            fit, virtualflies = self._model.fitflies( blob._body_image, blob._wings_image, virtualflies)
            for i, x in enumerate(virtualflies):
                x.draw(blobs[i]._image)
                min_angle = abs(minimumAngleBetween(blobs[i].angle_degrees, x.angleTailHead))
                if min_angle>90: blobs[i].flip()

        #Flies are merged and bodies are merged
        elif self._flies_bodies_split==2:
            pass
        return blobs

    def process(self, blobs):
        blobs = super(OTPFliesPostureEstimator, self).process(blobs)
        return OTPFliesPostureEstimator.compute(self, blobs)
