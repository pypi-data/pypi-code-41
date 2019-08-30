
import cv2, numpy as np

class Path(object):

    def __init__(self, blob):
        self._data = [blob]
        self._last_blob = blob
        self._path = []
        if blob: self._path.append(blob._centroid)
        
    def __len__(self): return len(self._data)
    def __getitem__(self, index): return self._data[index] if len(self._data)>index else None

    def clear(self): 
        self._data      = []
        self._last_blob = None

    def distance_to(self, blob):
        if self._last_blob is not None:
            return self._last_blob.distance_to(blob)
        return 999999999999999999999999

    def append(self, blob):
        if blob:
            self._last_blob = blob
            self._path.append(blob._centroid)
        self._data.append(blob)

    def draw(self, frame, color=(255,255,0)): 
        cv2.polylines(frame, np.array( [self._path] ), False, color, 2)

    @property
    def centroid(self): 
        if self._last_blob:
            return self._last_blob.centroid
        else:
            return None
    
    @property
    def path(self): return self._path