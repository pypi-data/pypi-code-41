import numpy as np
from tools import *
from OTPBase import OTPBase



class OTPBlobExtremePoints(OTPBase):

    def __init__(self, **kwargs):
        super(OTPBlobExtremePoints, self).__init__(**kwargs)


    def compute(self, blobs):        
        for blob in blobs:
            dists = map( lambda p: lin_dist( p[0], blob._centroid ), blob._contour )
            ndx = dists.index(max(dists))
            blob._head = tuple(blob._contour[ndx][0])
            
            dists = map( lambda p: lin_dist( p[0], blob._contour[ndx][0] ), blob._contour )
            ndx = dists.index(max(dists))

            blob._tail = tuple(blob._contour[ndx][0])

        return blobs

    def process(self, blobs):
        blobs = super(OTPBlobExtremePoints, self).process(blobs)
        return OTPBlobExtremePoints.compute(self, blobs)















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