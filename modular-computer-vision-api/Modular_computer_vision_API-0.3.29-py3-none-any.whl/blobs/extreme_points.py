import numpy as np
import math
from mcvapi.mcvbase import MCVBase

def lin_dist(p0, p1):   return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

class BlobExtremePoints(MCVBase):

    IMPORT = "from mcvapi.blobs.extreme_points import BlobExtremePoints"

    def load(self, data, **kwargs):
        super(BlobExtremePoints, self).load(data, **kwargs)


    def save(self, data, **kwargs):
        return super(BlobExtremePoints, self).save(data, **kwargs)


    def process(self, blobs, **kwargs):        
        for blob in blobs:
            dists = list(map( lambda p: lin_dist( p[0], blob._centroid ), blob._contour ))
            ndx = dists.index(max(dists))
            blob._head = tuple(blob._contour[ndx][0])
            
            dists = list(map( lambda p: lin_dist( p[0], blob._contour[ndx][0] ), blob._contour ))
            ndx = dists.index(max(dists))

            blob._tail = tuple(blob._contour[ndx][0])

        return blobs

    def processflow(self, blobs, **kwargs):
        blobs = super(BlobExtremePoints, self).processflow(blobs, **kwargs)
        return BlobExtremePoints.process(self, blobs, **kwargs)














'''
if __name__ == "__main__":
    import cv2
    capture = cv2.VideoCapture("/home/ricardo/Desktop/led30.avi")

    module = OTPBlobExtremePoints()

    while True:
        res, frame = capture.read()
        if not res: break;

        blobs = module.process(frame)
        for b in blobs: 
            b.draw(frame)
            cv2.circle(frame, b._centroid, 5,(255,0,255), 3)
            cv2.circle(frame, b._head, 5,(0,0,255), 3)
            cv2.circle(frame, b._tail, 5,(255,0,0), 3)

        cv2.imshow("Capture", frame)

        key = cv2.waitKey(1)
        if key == ord('q'): break
'''