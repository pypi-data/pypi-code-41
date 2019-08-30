import numpy as np, tools, math,cv2
from OTPBase import OTPBase
import Utils.ImageBlobTools as blobTools

class OTPCheckBlobDirectionByColor(OTPBase):
    """
    Put the blobs in quarantine until have sure about their direction
    Return: Blobs with direction
    """

    DIRECTION_WARNING_NO_HISTORY = 0
    DIRECTION_WARNING_WEAK = 1
    DIRECTION_WARNING_STRONG = 2

    def __init__(self, **kwargs):
        super(OTPCheckBlobDirectionByColor, self).__init__(**kwargs)
        self._history = []

    def __check_dir_head_tail(self, img):
        eroded_image = blobTools.cutBiggestContour( img ) 
        h,w = eroded_image.shape
        top = eroded_image[:int(h/4.0)]
        bottom = eroded_image[int( (h*3)/4.0):]
        return np.average( top[top!=0] )<np.average( bottom[bottom!=0] )
       

    def compute(self, blobs):

        if len(blobs)!=len(self._history):        
            for b in blobs:
                if min(b._axes)/max(b._axes)<=0.5:
                    if not self.__check_dir_head_tail(b._rotated_image): b.flip()
                    b._direction_checked = True
                else:
                    b._direction_checked = False
        else:
            for b1, b2 in zip( blobs, self._history):
                if b2._direction_checked:
                    if min(b1._axes)/max(b1._axes)>0.5:
                        b1._direction_checked = False
                    else:
                        b1._direction_checked = True
                else:
                    if min(b1._axes)/max(b1._axes)<=0.5:
                        if not self.__check_dir_head_tail(b1._rotated_image): b1.flip()
                        b1._direction_checked = True
                    else:
                        b1._direction_checked = False
           
        self._history = blobs
        return blobs

    def process(self, blobs):
        blobs = super(OTPCheckBlobDirectionByColor, self).process(blobs)
        return OTPCheckBlobDirectionByColor.compute(self, blobs)
