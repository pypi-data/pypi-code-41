import cv2
import numpy as np
from mcvapi.mcvbase import MCVBase

class BackgroundSubtract(MCVBase):
    
    IMPORT = "from mcvapi.filters.background_subtract import BackgroundSubtract"
    
    def __init__(self, **kwargs):
        super(BackgroundSubtract, self).__init__(**kwargs)

        

    def load(self, data, **kwargs):
        super(BackgroundSubtract, self).load(data, **kwargs)
        self._param_backgroundsubtract_image     = data.get('backgroundsubtract_image', None)
        self._param_backgroundsubtract_threshold = data.get('backgroundsubtract_threshold', 0)

    def save(self, data, **kwargs):
        data = super(BackgroundSubtract, self).save(data, **kwargs)
        data['backgroundsubtract_image']     = self._param_backgroundsubtract_image
        data['backgroundsubtract_threshold'] = self._param_backgroundsubtract_threshold
        return data

    #####################################################################
    ### FUNCTIONS #######################################################
    #####################################################################


    def process(self, frame, **kwargs):
        if len(frame.shape)>2: frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        background = self._param_backgroundsubtract_image

        if background is not None and len(background.shape)>2:
            background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        
        if background is not None and len(background)>1:
            diff        = cv2.absdiff(frame , background)
            ret , res   = cv2.threshold(diff, self._param_backgroundsubtract_threshold , 255, cv2.THRESH_BINARY )
            return res
        else:
            return np.zeros_like(frame)

    def processflow(self, image, **kwargs):
        res = super(BackgroundSubtract, self).processflow(image, **kwargs)
        return BackgroundSubtract.process(self, res, **kwargs)