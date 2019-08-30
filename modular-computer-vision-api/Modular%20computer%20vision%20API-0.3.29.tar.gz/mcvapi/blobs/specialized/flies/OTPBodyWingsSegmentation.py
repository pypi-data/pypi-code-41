from OTPBase import OTPBase
# from Blob import Blob
# import numpy as np, cv2, math
# import Utils.ImageBlobTools as blobTools
# from tools import *
# import numpy as np
import cv2
import numpy as np

from intelligence.threegaussianmodel import ThreeGaussianModel


class OTPBodyWingsSegmentation(OTPBase):

    def __init__(self, **kwargs):
        super(OTPBodyWingsSegmentation, self).__init__(**kwargs)
        self._threshModel = ThreeGaussianModel(hist_range=(0, 253))
        self._kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize=(3, 3))
        self._bodywingssegm_counter = -1

    def compute(self, blobs):
        
        for i, b in enumerate(blobs):
            oimage = b._oimage if len(b._oimage.shape)==2 else cv2.cvtColor(b._oimage, cv2.cv.CV_BGR2GRAY)
            
            try:
                #cv2.imshow('2blob'+str(i), oimage)
                if (self._bodywingssegm_counter>=60 or self._bodywingssegm_counter==-1):
                    self._bodywingssegm_counter = 0
                    self._threshModel.calc_thresholds(image=oimage, fit=True)
                else:
                    self._threshModel.calc_thresholds(image=oimage, fit=False)
                #self._threshModel.calc_thresholds(image=oimage, fit=True)
                     

                b._body_mask = self._threshModel.body_mask #cv2.morphologyEx(self._threshModel.body_mask, cv2.MORPH_OPEN, self._kernel)

                
                if len(self.bodies_contours(b._body_mask))==0:
                    self._threshModel.calc_thresholds(image=oimage, fit=True)
                    b._body_mask = self._threshModel.body_mask #cv2.morphologyEx(self._threshModel.body_mask, cv2.MORPH_OPEN, self._kernel)                

                b._wings_mask = self._threshModel.wings_mask #cv2.morphologyEx(self._threshModel.wings_mask, cv2.MORPH_OPEN, self._kernel)
            
            except:
                b._body_mask = np.zeros_like(b._oimage)
                b._wings_mask = np.zeros_like(b._oimage)

            #cv2.imshow('2blob'+str(i) +' body mask', b._body_mask)

            #cv2.imshow('2blob'+str(i) +' wings mask', b._wings_mask)

        #cv2.waitKey(1)

        self._bodywingssegm_counter +=1
        return blobs

    def process(self, blobs):
        blobs = super(OTPBodyWingsSegmentation, self).process(blobs)
        return OTPBodyWingsSegmentation.compute(self, blobs)
