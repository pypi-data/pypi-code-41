from mcvapi.mcvbase import MCVBase
import numpy as np, cv2


class PolygonsMask(MCVBase):
    
    IMPORT = "from mcvapi.masks.polygons_mask import PolygonsMask"
    
    def __init__(self, **kwargs):
        super(PolygonsMask, self).__init__(**kwargs)


    def load(self, data, **kwargs):
        super(PolygonsMask, self).load(data, **kwargs)
        self._param_polygonsmask_mask  = data.get('polygonsmask_mask')
        self._param_polygonsmask_polys = data.get('polygonsmask_polys')

    def save(self, data, **kwargs):
        data = super(PolygonsMask, self).save(data, **kwargs)
        data['polygonsmask_mask']  = self._param_polygonsmask_mask
        data['polygonsmask_polys'] = self._param_polygonsmask_polys
        return data

    def process(self, frame, **kwargs): 
        if self._param_polygonsmask_mask is None:
            self._param_polygonsmask_mask = np.zeros_like(frame)
            cv2.drawContours(self._param_polygonsmask_mask, self._param_polygonsmask_polys, -1, (255,255,255), -1)      
        return cv2.bitwise_and(frame, self._param_polygonsmask_mask)

    def processflow(self, frame, **kwargs):
        frame = super(PolygonsMask, self).processflow(frame, **kwargs)
        return PolygonsMask.process(self, frame, **kwargs)

    def clear(self): 
        self._param_polygonsmask_mask = None
        pass