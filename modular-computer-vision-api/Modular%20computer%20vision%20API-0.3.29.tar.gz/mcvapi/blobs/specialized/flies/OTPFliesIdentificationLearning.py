from OTPBase import *
from Blob import Blob
import cv2, numpy as np

class OTPFliesIdentificationLearning(OTPBase):
    """
    Return a list of blobs
    """

    def __init__(self, **kwargs):
        super(OTPFliesIdentificationLearning, self).__init__(**kwargs)
        self._svm = cv2.SVM()
        self._first = True
        self.params = dict( kernel_type = cv2.SVM_RBF,svm_type = cv2.SVM_C_SVC,C = 1,gamma = 0.5 )

    def compute(self, blobs):

        if self._flies_bodies_split==0:

            """
            if not self._first:
                for i, blob in enumerate(blobs):
                    #sample = np.float32([blob.height, blob.body_area])
                    #sample = np.float32([blob.body_area, blob.height])
                    sample = np.float32([blob.height])
                    #sample = np.float32([blob.body_area])
                    prediction = self._svm.predict( sample )

                    if i!=int(prediction):
                        print "blob", i, 'was predicted with', prediction
            else:
                self._first = False
            """
            trainData = []
            responses = []
            for i, blob in enumerate(blobs):
                #sample = np.float32([blob.height, blob.body_area])
                #sample = np.float32([blob.body_area, blob.height])
                sample = np.float32([blob.height])
                #sample = np.float32([blob.body_area])
                trainData.append( sample )
                responses.append(i)

            self._svm.train(np.float32(trainData),np.float32(responses), params = self.params)
            
    
                
        return blobs
        

    def process(self, frame):
        frame = super(OTPFliesIdentificationLearning, self).process(frame)
        return OTPFliesIdentificationLearning.compute(self,frame)
