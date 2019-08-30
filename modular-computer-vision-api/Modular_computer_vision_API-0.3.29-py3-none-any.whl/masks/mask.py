from mcvapi.mcvbase import MCVBase
import numpy as np, cv2


class Mask(MCVBase):
    
    IMPORT = "from mcvapi.masks.mask import Mask"
    
    def __init__(self, **kwargs):
        super(Mask, self).__init__(**kwargs)


    def load(self, data, **kwargs):
        super(Mask, self).load(data, **kwargs)
        self._param_mask_img  = data.get('mask_img', None)

    def save(self, data, **kwargs):
        data = super(Mask, self).save(data, **kwargs)
        data['mask_img']  = self._param_mask_img
        return data


    def process(self, frame, **kwargs):
        if self._param_mask_img is not None:
            if len(frame.shape)==2:
                return cv2.bitwise_and(frame, self._param_mask_img)
            else:
                a,b,c = cv2.split(frame)
                a = cv2.bitwise_and(a, self._param_mask_img)
                b = cv2.bitwise_and(b, self._param_mask_img)
                c = cv2.bitwise_and(c, self._param_mask_img)
                return cv2.merge( (a,b,c) )
        else:
            return frame

    def processflow(self, frame, **kwargs):
        frame = super(Mask, self).processflowself(frame, **kwargs)
        return Mask.process(self, frame, **kwargs)    