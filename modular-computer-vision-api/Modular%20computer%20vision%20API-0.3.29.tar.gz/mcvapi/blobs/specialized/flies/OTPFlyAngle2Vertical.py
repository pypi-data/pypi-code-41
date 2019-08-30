import numpy as np
from tools import *
from OTPBase import OTPBase
from OTPBlobAngle2Vertical import OTPBlobAngle2Vertical
import pyforms.Utils.tools as tools
import Utils.ImageBlobTools as blobTools
import cv2
import math

class OTPFlyAngle2Vertical(OTPBlobAngle2Vertical):

    def compute(self, blobs):
        blobs_2_remove = []
        for blob in blobs:
            p1, p2 = blob._bounding
            mask = self._in_original_image[p1[1]:p2[1], p1[0]:p2[0]]
            _, mask = cv2.threshold(mask, 80,255,cv2.THRESH_BINARY_INV)
            
        
            contour = blobTools.getBiggestContour( mask )
            if contour==None:contour = blob._contour
            
            if contour==None or len(contour)<5: 
                blobs_2_remove.append(blob)
                continue
            center,axes,orientation = cv2.fitEllipse(contour)

            blob._axes = axes
            blob._angle_2_vertical_degrees = orientation + 90
            blob._angle_2_vertical_rad = math.radians( orientation +90)

            m = cv2.moments(contour);m00 = m['m00']
            if m00!=0: centroid = (p1[0]+ int(round(m['m10']/m00) ), int(p1[1]+round(m['m01']/m00)) )
            else: centroid = (p1[0],p1[1])

            blob._centroid = centroid
            
            angle = blob._angle_2_vertical_rad
            max_axis = float(max(axes)/2)

            blob._head = int(max_axis*math.cos(angle)+centroid[0]), int(max_axis*math.sin(angle)+centroid[1])
            blob._tail = int(max_axis*math.cos(angle+math.pi)+centroid[0]), int(max_axis*math.sin( angle+math.pi )+centroid[1])
            
        for blob in blobs_2_remove:blobs.remove(blob)
        return blobs

    def process(self, blobs):
        blobs = super(OTPFlyAngle2Vertical, self).process(blobs)
        return OTPFlyAngle2Vertical.compute(self, blobs)