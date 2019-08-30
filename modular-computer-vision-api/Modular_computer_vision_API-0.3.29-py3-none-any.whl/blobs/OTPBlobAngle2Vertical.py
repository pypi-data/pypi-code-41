import numpy as np
from tools import *
from OTPBase import OTPBase
import pyforms.Utils.tools as tools
import Utils.ImageBlobTools as blobTools


class OTPBlobAngle2Vertical(OTPBase):

    def __init__(self, **kwargs):
        super(OTPBlobAngle2Vertical, self).__init__(**kwargs)
        self._element = cv2.getStructuringElement(cv2.MORPH_CROSS,(15,15))

    def compute(self, blobs):
        blobs_2_remove = []
        for blob in blobs:
            p1, p2 = blob._bounding
            mask = self._out_segmented_image[p1[1]:p2[1], p1[0]:p2[0]]
            eroded_image = cv2.erode(mask,self._element)
            #eroded_image = cv2.blur(mask, (45,45) )
            #_,eroded_image = cv2.threshold(eroded_image, 200,255,cv2.THRESH_BINARY)
            
            contour = blobTools.getBiggestContour( eroded_image )
            if contour==None: 
                blobs_2_remove.append(blob)
                continue

            m = cv2.moments(contour); m00 = m['m00']
            if m00!=0: centroid = ( int(round(m['m10']/m00) ), int(round(m['m01']/m00)) )
            else: centroid = (0,0)

            dists = map( lambda p: tools.lin_dist( p[0], centroid ), contour )
            ndx = dists.index(max(dists))
            head = tuple( contour[ndx][0] )
            dists = map( lambda p: tools.lin_dist( p[0], contour[ndx][0] ), contour )
            ndx = dists.index(max(dists))
            tail = tuple( contour[ndx][0] )
            
            blob._angle_2_vertical_rad = tools.points_angle(head,tail) + 1
            blob._angle_2_vertical_degrees = math.degrees( blob._angle_2_vertical_rad ) 

        for blob in blobs_2_remove:blobs.remove(blob)
        return blobs

    def process(self, blobs):
        blobs = super(OTPBlobAngle2Vertical, self).process(blobs)
        return OTPBlobAngle2Vertical.compute(self, blobs)