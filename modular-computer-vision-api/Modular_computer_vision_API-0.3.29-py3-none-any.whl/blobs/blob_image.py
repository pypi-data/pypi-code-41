import numpy as np
import math
from mcvapi.mcvbase import MCVBase


class BlobImage(MCVBase):

    IMPORT = "from mcvapi.blobs.blob_image import BlobImage"

    def load(self, data, **kwargs):
        super(BlobImage, self).load(data, **kwargs)
        self._param_blobimage_margin = data.get('blobimage_margin', 0)
        

    def save(self, data, **kwargs):
        data = super().save(data, **kwargs)
        data['blobimage_margin'] = self._param_blobimage_margin
        return data

    def process(self, blobs, **kwargs):
        _in_original_image = kwargs['oimage']
        for blob in blobs:
            p1, p2 = blob._bounding
            margin = self._param_blobimage_margin
            cut_x, cut_y, cut_xx, cut_yy = p1[0]-margin, p1[1]-margin, p2[0]+margin, p2[1]+margin
            if cut_x<0: cut_x=0
            if cut_y<0: cut_y=0
            if cut_xx>_in_original_image.shape[1]: cut_xx=_in_original_image.shape[1]
            if cut_yy>_in_original_image.shape[0]: cut_yy=_in_original_image.shape[0]

            partial_image = _in_original_image[cut_y:cut_yy, cut_x:cut_xx]
            
            blob._oimage = partial_image
            
            
        return blobs

    def processflow(self, blobs, **kwargs):
        blobs = super(BlobImage, self).processflow(blobs, **kwargs)
        return BlobImage.process(self, blobs, **kwargs)

