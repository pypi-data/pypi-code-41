import cv2
from mcvapi.mcvbase import MCVBase
from mcvapi.blobs.blob import Blob

class FindBlobs(MCVBase):
   
    IMPORT = "from mcvapi.blobs.find_blobs import FindBlobs"
    

    def load(self, data, **kwargs):
        super(FindBlobs, self).load(data, **kwargs)
        self._param_findblobs_min_area = data.get('findblobs_min_area', 0)
        self._param_findblobs_max_area = data.get('findblobs_max_area', 100000000)
        

    def save(self, data, **kwargs):
        data = super(FindBlobs, self).save(data, **kwargs)
        data['findblobs_min_area'] = self._param_findblobs_min_area
        data['findblobs_max_area'] = self._param_findblobs_max_area
        return data

    def process(self, frame, **kwargs):
        _, contours, _ = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        objectsFound = []
        for cnt in contours:
            m = cv2.moments(cnt); m00 = m['m00']
            
            if self._param_findblobs_min_area <= m00 <= self._param_findblobs_max_area:
                if m00!=0: centroid = ( int(round(m['m10']/m00) ), int(round(m['m01']/m00)) )
                else: centroid = (0,0)

                box = cv2.boundingRect(cnt)
                p1, p2 = (box[0], box[1]), (box[0]+box[2], box[1]+box[3])
        
                obj = Blob()
                obj._contour    = cnt
                obj._bounding   = (p1, p2)
                obj._area       = m00
                obj._centroid   = centroid
                objectsFound.append( obj )

        return objectsFound

    def processflow(self, frame, **kwargs):
        blobs = super(FindBlobs, self).processflow(frame, **kwargs)
        return FindBlobs.process(self, blobs, **kwargs)