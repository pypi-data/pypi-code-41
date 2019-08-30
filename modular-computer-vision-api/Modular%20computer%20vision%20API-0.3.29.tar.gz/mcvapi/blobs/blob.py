import numpy as np, cv2, math

class Blob(object):

    def __init__(self):
        self._contour   = None
        self._centroid  = None
        self._bounding  = None
        self._area      = None

    def draw(self, frame, color=(255,255,0)):
        cv2.polylines(frame, np.array( [self._contour] ), True, color, 2)

        if hasattr(self, '_head') and hasattr(self, '_tail'):
            cv2.circle(frame, self._head, 3, (0,0,255), -1)
            cv2.circle(frame, self._tail, 3, (255,0,0), -1)

    def distance_to(self, blob):
        p0 = self._centroid
        p1 = blob._centroid
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def angle_between(self, previous_blob, next_blob):
        if isinstance( previous_blob, tuple ) and isinstance( next_blob, tuple ):
            pt0, pt1, pt2 = previous_blob, self._centroid, next_blob
        else:
            pt0, pt1, pt2 = previous_blob._centroid, self._centroid, next_blob._centroid
        dx1 = pt0[0] - pt1[0]
        dy1 = pt0[1] - pt1[1]
        dx2 = pt2[0] - pt1[0]
        dy2 = pt2[1] - pt1[1]
        nom = dx1*dx2 + dy1*dy2
        denom = math.sqrt( (dx1*dx1 + dy1*dy1) * (dx2*dx2 + dy2*dy2) + 1e-10 )
        ang = nom / denom
        return math.degrees( math.acos(ang) )

    @property
    def centroid(self): return self._centroid