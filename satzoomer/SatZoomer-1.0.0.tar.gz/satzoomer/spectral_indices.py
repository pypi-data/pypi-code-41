from skimage.io import imread
import numpy as np
from utils import eight_bit_stretch

def ndvi(irg, threshold=False):
    """
    Returns the Normalized Difference Vegetation Index for an IRG image
    """
    nir, red = irg[:,:,0].astype(np.float32), irg[:,:,1].astype(np.float32)
    ndvi_with_nan = (nir - red) / (nir + red)
    ndvi = np.nan_to_num(ndvi_with_nan)
    if threshold:
        threshed = np.where(ndvi > 0, ndvi, 0)
        ndvi = eight_bit_stretch(threshed, lower_bound=0, upper_bound=1)
    return ndvi

def ndwi(irg, threshold=0.4):
    """
    Returns the Normalized Difference Water Index for an IRG image
    """
    green, nir = irg[:,:,2].astype(np.float32), irg[:,:,0].astype(np.float32)
    ndwi_with_nan = (green - nir) / (green + nir)
    ndwi_no_nan = np.nan_to_num(ndwi_with_nan)
    if threshold:
        threshed = np.where(ndwi_no_nan > threshold, ndwi_no_nan, threshold)
        ndwi_out = eight_bit_stretch(threshed, lower_bound=threshold, upper_bound=1)
    return ndwi_out

def bare_soil_index(rgb):
    """
    Returns the Bare Soil Index for an RGB image
    """
    r, g, b = rgb[:,:,0].astype(np.float32), rgb[:,:,1].astype(np.float32), rgb[:,:,2].astype(np.float32)
    bi_with_nan = (r + b - g) / (r + b + g)
    bi_no_nan = np.nan_to_num(bi_with_nan)
    stretched = eight_bit_stretch(bi_no_nan, lower_bound=-1, upper_bound=1)
    return stretched