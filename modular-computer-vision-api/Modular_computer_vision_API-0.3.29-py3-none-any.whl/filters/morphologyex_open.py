import cv2
import numpy as np
from mcvapi.mcvbase import MCVBase

class MorphologyExOpen(MCVBase):
    
    IMPORT = "from mcvapi.filters.morphologyex_open import MorphologyExOpen"
    
    def __init__(self, **kwargs):
        super(MorphologyExOpen, self).__init__(**kwargs)


    def load(self, data, **kwargs):
        super(MorphologyExOpen, self).load(data, **kwargs)
        self._param_morphologyexopen_kernel_size = data.get('morphologyexopen_kernel_size', 3)
        self._param_morphologyexopen_kernel      = np.ones(
            (self._param_morphologyexopen_kernel_size,self._param_morphologyexopen_kernel_size)
            ,np.uint8
        )
        self._param_morphologyexopen_usefilter = data.get('morphologyexopen_usefilter', False)

    def save(self, data, **kwargs):
        data = super(MorphologyExOpen, self).save(data, **kwargs)
        data['morphologyexopen_kernel_size'] = self._param_morphologyexopen_kernel_size
        data['morphologyexopen_usefilter'] = self._param_morphologyexopen_usefilter
        return data

    #####################################################################
    ### FUNCTIONS #######################################################
    #####################################################################


    def process(self, frame, **kwargs):
        if self._param_morphologyexopen_usefilter:
            return cv2.morphologyEx(frame, cv2.MORPH_OPEN, self._param_morphologyexopen_kernel)
        else:
            return frame

    def processflow(self, image, **kwargs):
        res = super(MorphologyExOpen, self).processflow(image, **kwargs)
        return MorphologyExOpen.process(self, res, **kwargs)