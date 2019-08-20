import numpy as np

def convert_to_colour(arr_2d, palette):
    """ Numeric labels to RGB-color encoding """
    arr_3d = np.zeros((arr_2d.shape[0], arr_2d.shape[1], 3), dtype=np.uint8)

    for c, i in palette.items():
        m = arr_2d == c
        arr_3d[m] = i

    return arr_3d

def convert_from_colour(arr_3d, palette):
    """ RGB-color encoding to grayscale labels """
    arr_2d = np.zeros((arr_3d.shape[0], arr_3d.shape[1]), dtype=np.uint8)

    for c, i in palette.items():
        m = np.all(arr_3d == np.array(c).reshape(1, 1, 3), axis=2)
        arr_2d[m] = i

    return arr_2d

def eight_bit_stretch(img, lower_bound, upper_bound):
    """ Stretches image to be 8-bit """
    stretched = 255 * (img - lower_bound) / (upper_bound - lower_bound)
    return stretched.astype(np.uint8)

