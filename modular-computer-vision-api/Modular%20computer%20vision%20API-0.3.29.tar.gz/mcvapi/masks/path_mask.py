from mcvapi.mcvbase import MCVBase
import numpy as np, cv2


class PathMask(MCVBase):
    
    IMPORT = "from mcvapi.masks.path_mask import PathMask"
    
    def __init__(self, **kwargs):
        super(PathMask, self).__init__(**kwargs)


    def load(self, data, **kwargs):
        super(PathMask, self).load(data, **kwargs)
        self._param_pathmask_paths  = data.get('pathmask_paths', [])
        self._param_pathmask_radius = data.get('pathmask_radius', 30)
       
    def save(self, data, **kwargs):
        data = super(PathMask, self).save(data, **kwargs)
        data['pathmask_paths']  = self._param_pathmask_paths
        data['pathmask_radius'] = self._param_pathmask_radius
        return data

    def process(self, frame, **kwargs):
        paths = self._param_pathmask_paths
        mask  = np.zeros_like(frame)

        frame_index = kwargs.get('frame_index')

        for path in paths:
            position = path[frame_index] if isinstance(path, list) else path.get_position(frame_index) 
            if position is not None: cv2.circle(mask, position, self._param_pathmask_radius, (255,255,255), -1)         
        return cv2.bitwise_and(frame, mask)

    def processflow(self, frame, **kwargs):
        frame = super(PathMask, self).processflow(frame, **kwargs)
        return PathMask.process(self, frame, **kwargs)