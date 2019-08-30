import cv2
from mcvapi.mcvbase import MCVBase

# for compatibility between opencv 2 and 3
try:
    # OpenCV 2
    CV_ADAPTIVE_THRESH_MEAN_C = cv2.cv.CV_ADAPTIVE_THRESH_MEAN_C
    THRESH_BINARY             = cv2.cv.CV_THRESH_BINARY
except:
    # OpenCV 3
    CV_ADAPTIVE_THRESH_MEAN_C = cv2.ADAPTIVE_THRESH_MEAN_C
    THRESH_BINARY             = cv2.THRESH_BINARY


class AdaptativeThreshold(MCVBase):
    
    IMPORT = "from mcvapi.filters.adaptative_threshold import AdaptativeThreshold"
    
    def __init__(self, **kwargs):
        super(AdaptativeThreshold, self).__init__(**kwargs)



    def load(self, data, **kwargs):
        super(AdaptativeThreshold, self).load(data, **kwargs)
        self._param_adaptivethreshold_method        = data.get('adaptivethreshold_method', CV_ADAPTIVE_THRESH_MEAN_C )
        self._param_adaptivethreshold_type          = data.get('adaptivethreshold_type', THRESH_BINARY)
        self._param_adaptivethreshold_block_size    = data.get('adaptivethreshold_block_size', 3)
        self._param_adaptivethreshold_c             = data.get('adaptivethreshold_c', 255)

    def save(self, data, **kwargs):
        data = super(AdaptativeThreshold, self).save(data, **kwargs)
        data['adaptivethreshold_method']        = self._param_adaptivethreshold_method
        data['adaptivethreshold_type']          = self._param_adaptivethreshold_type
        data['adaptivethreshold_block_size']    = self._param_adaptivethreshold_block_size
        data['adaptivethreshold_c']             = self._param_adaptivethreshold_c
        return data
    #####################################################################
    ### PROPERTIES ######################################################
    #####################################################################

    def __adaptivethreshold_block_size(self):    
        if (self._param_adaptivethreshold_block_size % 2)==0: 
            self._param_adaptivethreshold_block_size += 1
        return self._param_adaptivethreshold_block_size

    #####################################################################
    ### FUNCTIONS #######################################################
    #####################################################################


    def process(self, frame, **kwargs):
        thresh = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY) if len(frame.shape)>2 else frame
        
        return cv2.adaptiveThreshold(
            thresh, 255,
            self._param_adaptivethreshold_method,
            self._param_adaptivethreshold_type,
            self.__adaptivethreshold_block_size(),
            self._param_adaptivethreshold_c
        )

    def processflow(self, image, **kwargs):
        res = super(AdaptativeThreshold, self).processflow(image, **kwargs)
        return AdaptativeThreshold.process(self, res, **kwargs)