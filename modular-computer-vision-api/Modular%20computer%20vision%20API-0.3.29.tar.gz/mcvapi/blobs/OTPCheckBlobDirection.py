import numpy as np, tools, math,cv2
from OTPBase import OTPBase
import Utils.ImageBlobTools as blobTools

class OTPCheckBlobDirection(OTPBase):
    """
    Put the blobs in quarantine until have sure about their direction
    Return: Blobs with direction
    """

    DIRECTION_WARNING_NO_HISTORY = 0
    DIRECTION_WARNING_WEAK = 1
    DIRECTION_WARNING_STRONG = 2

    def __init__(self, **kwargs):
        super(OTPCheckBlobDirection, self).__init__(**kwargs)

        self._history = []
        

    def __mark_no_detection(self, blobs):
        for blob in blobs: 
            blob._direction_flag = self.DIRECTION_WARNING_NO_HISTORY

    def __is_correct_direction(self, history, blob_index):
        if len(history)<5: return False

        first_blob = history[0]
        last_blob = first_blob

        distance_walked = 0
        translated_distance = 0
        directional_walk = 0
        
        for blob in history[1:]:
            if  315<=math.degrees(blob._movement_angle)<=45 or \
                135<=math.degrees(blob._movement_angle)<=225:
                distance_walked += abs(blob._velocity)
                translated_distance += tools.lin_dist(first_blob._centroid, blob._centroid)
                directional_walk += blob._velocity

        if abs(directional_walk)>10 and \
           translated_distance>100 and \
           distance_walked>100:
            if directional_walk<0:
                for blob in history: blob.flip()
            #   print "Blob:", blob_index, 'Flipped', distance_walked, translated_distance, directional_walk
            #else:
            #   print "Blob:", blob_index, distance_walked, translated_distance, directional_walk
            
           
        else:
            count = 0
                
            for b in history:
                if min(b._axes)/max(b._axes)<=0.7:
                    img = b._rotated_image
                    eroded_image = blobTools.cutBiggestContour( img ) 
                    h,w = eroded_image.shape
                    top = eroded_image[:int(h/2.0)]
                    bottom = eroded_image[int(h/2.0):]

                    if np.average( top[top!=0] )>np.average( bottom[bottom!=0] ): count+=1
                    else: count-=1

            if count>0:
                for b in history: b.flip()
        """
        b = history[-1]
        b.draw(self._in_original_image)

        cv2.circle( self._in_original_image, first_blob._centroid, 16, 255, 2)
        cv2.circle( self._in_original_image, b._centroid, 8, 150, 2)

        cv2.circle( self._in_original_image, b._head, 4, (0, 0, 255), 4)
        cv2.circle( self._in_original_image, b._tail, 4, (0, 255, 0), 4)
        b.draw_properties(self._in_original_image)
        cv2.imshow("flies", self._in_original_image )
        cv2.waitKey(0)
        """

    def compute(self, blobs):

        if  len(blobs)!=len(self._history):

            if len(self._history)>1:
                for i, blobs_history in enumerate(self._history):  
                    self.__is_correct_direction( blobs_history, i )

            self._history = [[b] for b in blobs]
        elif len(blobs)>1:
            """ When the current number and the past number of blobs are equal"""
        
            for i, (blob, last_blobs) in enumerate( zip(blobs, self._history) ):
                

                check_dir = False
                if (min(blob._axes)/max(blob._axes))>0.7: check_dir=True
                #if abs(current_blob._velocity)>30: check_dir=True

                if check_dir:
                    self.__is_correct_direction(last_blobs, i)
                    del last_blobs[:]
                    last_blobs.append(blob)
                else:
                    last_blobs.append(blob)
              
        return blobs

    def process(self, blobs):
        blobs = super(OTPCheckBlobDirection, self).process(blobs)
        return OTPCheckBlobDirection.compute(self, blobs)
