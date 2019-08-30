import cv2
import numpy as np
from mcvapi.mcvbase import MCVBase

class MorphologyExClose(MCVBase):
    
    IMPORT = "from mcvapi.filters.morphologyex_close import MorphologyExClose"
    
    def __init__(self, **kwargs):
        super(MorphologyExClose, self).__init__(**kwargs)


        

    def load(self, data, **kwargs):
        super(MorphologyExClose, self).load(data, **kwargs)
        self._param_morphologyexclose_kernel_size = data.get('morphologyexopen_kernel_size', 3)
        self._param_morphologyexclose_kernel = np.ones(
            (self._param_morphologyexclose_kernel_size,self._param_morphologyexclose_kernel_size)
            ,np.uint8
        )
        self._param_morphologyexclose_usefilter = data.get('morphologyexclose_usefilter', False)

    def save(self, data, **kwargs):
        data = super(MorphologyExClose, self).save(data, **kwargs)
        data['morphologyexopen_kernel_size'] = self._param_morphologyexclose_kernel_size
        data['morphologyexclose_usefilter'] = self._param_morphologyexclose_usefilter
        return data

    #####################################################################
    ### FUNCTIONS #######################################################
    #####################################################################


    def process(self, frame, **kwargs):
        if self._param_morphologyexclose_usefilter:
            return cv2.morphologyEx(frame, cv2.MORPH_CLOSE, self._param_morphologyexclose_kernel)
        else:
            return frame
        
    def processflow(self, image, **kwargs):
        res = super(MorphologyExClose, self).processflow(image, **kwargs)
        return MorphologyExClose.process(self, res, **kwargs)