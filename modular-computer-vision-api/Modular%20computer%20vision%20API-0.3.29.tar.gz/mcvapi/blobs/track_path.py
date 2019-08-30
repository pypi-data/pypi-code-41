from mcvapi.blobs.path import Path
from mcvapi.mcvbase import MCVBase

class TrackPath(MCVBase):
    
    # Group blobs by their path

    IMPORT = "from mcvapi.blobs.track_path import TrackPath"
    
    def __init__(self, **kwargs):
        super(TrackPath, self).__init__(**kwargs)
        self._trackpath_paths = []

    
    def clear(self): self._trackpath_paths = []

    def process(self, blobs, **kwargs):
        
        # First time
        if len(self._trackpath_paths)==0 or len(self._trackpath_paths)!=len(blobs): 
            self._trackpath_paths = [Path(b) for b in blobs]            
        elif len(blobs)>0:
            for i, b in enumerate(blobs): self._trackpath_paths[i].append(b)
        else:
            for i in len(self._trackpath_paths): self._trackpath_paths[i].append(None)

        return self._trackpath_paths

    def processflow(self, blobs, **kwargs):
        blobs = super(TrackPath, self).processflow(blobs, **kwargs)
        return TrackPath.process(self, blobs, **kwargs)
