import cv2, numpy as np
from mcvapi.mcvbase import MCVBase

class BackgroundDetector(MCVBase):

    _background                 = None
    _background_color           = [None,None,None]
    _background_sum             = [None,None,None]
    _background_average         = [None,None,None]
    _background_counter         = [None,None,None]
    _gaussian_blur_matrix_size  = None
    _gaussian_blur_sigma_x      = None
    _capture                    = None
    _width                      = 0
    _height                     = 0
    _update_function            = None

    _param_bgdetector_no_cache      = True
    _param_bgdetector_threshold     = 5
    _param_bgdetector_jump          = 30
    _param_bgdetector_compare_jump  = 500

    
    def __init__(self,**kwargs):
        super(BackgroundDetector, self).__init__(**kwargs)

        capture=None; gaussian_blur_matrix_size=3; gaussian_blur_sigma_x=5; update_function=None

        if "gaussian_blur_matrix_size" in kwargs.keys():    gaussian_blur_matrix_size = kwargs['gaussian_blur_matrix_size']
        if "gaussian_blur_sigma_x" in kwargs.keys():        gaussian_blur_sigma_x = kwargs['gaussian_blur_sigma_x']
        if "update_function" in kwargs.keys():              update_function = kwargs['update_function']
        if "capture" not in kwargs.keys(): 
            print( "The variable capture was not set in the object constructer")
            exit()
        else: 
            capture = kwargs['capture']
        
        self._width                     = int(round(capture.get( cv2.CAP_PROP_FRAME_WIDTH )))
        self._height                    = int(round(capture.get( cv2.CAP_PROP_FRAME_HEIGHT)))
        self._capture                   = capture
        self._gaussian_blur_matrix_size = gaussian_blur_matrix_size
        self._gaussian_blur_sigma_x     = gaussian_blur_sigma_x
        self._update_function           = update_function
        self.__initialize__()

    def __initialize__(self):
        cp = np.zeros( ( self._height, self._width ), np.float32 )
        self._background_sum     = [cp.copy(),cp.copy(),cp.copy()]
        self._background_counter = [cp.copy(),cp.copy(),cp.copy()]

    ############################################################################
    ### Workflow functions #####################################################
    ############################################################################

    def compute(self, frame):
        if self._background==None:
            if not self._param_bgdetector_no_cache:
                self._background = cv2.imread("gray_background.png", 0)
                self._background_color = cv2.imread("color_background.png", 1)
            if self._background==None or self._background_color==None:
                self.detect( self._param_bgdetector_jump, self._param_bgdetector_compare_jump, self._param_bgdetector_threshold )
                cv2.imwrite("gray_background.png",self.background)
                cv2.imwrite( "color_background.png",self.background_color)
        return frame

    def process(self, frame):
        frame = super(BackgroundDetector, self).process(frame)
        return BackgroundDetector.compute(self, frame)

    ############################################################################
    ### Internal functions #####################################################
    ############################################################################

    def __clean_noise(self, frame):
        """
        originalYCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
        Y, Cr, Cb = cv2.split(originalYCrCb)
        Y  = cv2.GaussianBlur(Y,  (self._gaussian_blur_matrix_size,self._gaussian_blur_matrix_size) self._gaussian_blur_sigma_x
        Cr = cv2.GaussianBlur(Cr, (self._gaussian_blur_matrix_size,self._gaussian_blur_matrix_size) self._gaussian_blur_sigma_x
        Cb = cv2.GaussianBlur(Cb, (self._gaussian_blur_matrix_size,self._gaussian_blur_matrix_size) self._gaussian_blur_sigma_x
        return Y, Cr, Cb
        """
        return cv2.split(frame)

    def __process(self, frame, jump_2_frame=2000, compare_with_jump_frame = 1000, threshold = 5 ):

        current_frame_index = self._capture.get( cv2.CAP_PROP_POS_FRAMES )
        Y, Cr, Cb           = self.__clean_noise(frame)
        
        #get the frame to which the current frame is going to be compared.
        self._capture.set( cv2.CAP_PROP_POS_FRAMES, current_frame_index + compare_with_jump_frame )
        res, next_frame = self._capture.read()

        if not res: return False

        #point the video capture to the next frame to test
        self._capture.set( cv2.CAP_PROP_POS_FRAMES, current_frame_index + jump_2_frame )


        
        if self._update_function!=None and \
            self._background_average[0] is not None and \
            self._background_average[1] is not None and \
            self._background_average[2] is not None:
            
            a = cv2.convertScaleAbs(self._background_average[0])
            b = cv2.convertScaleAbs(self._background_average[1])
            c = cv2.convertScaleAbs(self._background_average[2])
            tmp = cv2.merge( (a, b, c) )
            self._update_function( tmp, int(self._capture.get(cv2.CAP_PROP_POS_FRAMES)) )
        
        if res==False: return None
        Y_next, Cr_next, Cb_next = self.__clean_noise(next_frame)
        Y_diff, Cr_diff, Cb_diff = cv2.absdiff( Y, Y_next ), cv2.absdiff( Cr, Cr_next ), cv2.absdiff( Cb, Cb_next )
        
        ret , Y_gray  = cv2.threshold(Y_diff,  threshold , 255, cv2.THRESH_BINARY )
        ret , Cr_gray = cv2.threshold(Cr_diff, threshold , 255, cv2.THRESH_BINARY )
        ret , Cb_gray = cv2.threshold(Cb_diff, threshold , 255, cv2.THRESH_BINARY )
        
        _, contours, hierarchy = cv2.findContours(Y_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        hulls = []
        for contour in contours: hulls.append( cv2.convexHull( contour ) )
        
        Y_background_area  = np.ones( (self._height, self._width), np.float32 )
        Cr_background_area = Y_background_area.copy()
        Cb_background_area = Y_background_area.copy()

        cv2.drawContours( Y_background_area,  np.array( hulls ) , -1, (0), -1 )
        cv2.drawContours( Cr_background_area, np.array( hulls ) , -1, (0), -1 )
        cv2.drawContours( Cb_background_area, np.array( hulls ) , -1, (0), -1 )

        if __name__ == "__main__": cv2.imshow("hulls", background_area * 255)

        self._background_counter[0] += Y_background_area
        self._background_counter[1] += Cr_background_area
        self._background_counter[2] += Cb_background_area

        Y, Cr, Cb = cv2.split(frame)
        self._background_sum[0] += Y*Y_background_area
        self._background_sum[1] += Cr*Cr_background_area
        self._background_sum[2] += Cb*Cb_background_area

        np.seterr(all ='ignore')
        self._background_average[0] = np.divide(self._background_sum[0] , self._background_counter[0] )
        self._background_average[1] = np.divide(self._background_sum[1] , self._background_counter[1] )
        self._background_average[2] = np.divide(self._background_sum[2] , self._background_counter[2] )
    
        return True


    def detect(self, jump_2_frame=0, compare_with_jump_frame = 1000, threshold = 5 ):
        self.__initialize__()
        self._capture.set( cv2.CAP_PROP_POS_FRAMES, 0 )
        res = True
        old_state = np.seterr(all ='ignore')
        while res:
            res, current_frame = self._capture.read()
            if not res: break
            if not self.__process(current_frame, jump_2_frame, compare_with_jump_frame, threshold): break

        self._background        = cv2.convertScaleAbs(self._background_average[0])
        self._background_color  = cv2.merge( (cv2.convertScaleAbs(self._background_average[0]), cv2.convertScaleAbs(self._background_average[1]), cv2.convertScaleAbs(self._background_average[2])))

        self._capture.set( cv2.CAP_PROP_POS_FRAMES, 0 )
        np.seterr(**old_state)
        
        return self.background

    def quick_detect(self): self.detect(1000, 1500, 5)

    def subtract( self, frame, threshold=20, thresholdValue=255 ):
        diff = cv2.absdiff(frame , self._background_color)
        ret , res = cv2.threshold(diff, threshold , 255, cv2.THRESH_BINARY )
        diff = cv2.bitwise_and(frame, res)
        return diff

    ############################################################################
    ### Properties #############################################################
    ############################################################################

    @property
    def background(self): return self._background

    @property
    def background_color(self): return self._background_color


    ############################################################################
    ### IO Functions ###########################################################
    ############################################################################
    
    def save( self, data ):
        data['_background']                 = self._background
        data['_background_sum']             = self._background_sum
        data['_background_sum']             = self._background_average
        data['_background_counter']         = self._background_counter
        data['_gaussian_blur_matrix_size']  = self._gaussian_blur_matrix_size
        data['_gaussian_blur_sigma_x']      = self._gaussian_blur_sigma_x
        data['_width']                      = self._width
        data['_height']                     = self._height

    def load( self, data ):
        self._background                = data.get('_background', self._background)
        self._background_sum            = data.get('_background_sum', self._background_sum)
        self._background_average        = data.get('_background_average', self._background_average)
        self._background_counter        = data.get('_background_counter', self._background_counter)
        self._gaussian_blur_matrix_size = data.get('_gaussian_blur_matrix_size', self._gaussian_blur_matrix_size)
        self._gaussian_blur_sigma_x     = data.get('_gaussian_blur_sigma_x', self._gaussian_blur_sigma_x)
        self._width                     = data.get('_width', self._width)
        self._height                    = data.get('_height', self._height)