"""
Jacob Thompson

misc
"""
import numpy as np
from matplotlib import pyplot as plot
from skimage.transform import resize

def ImagePad(image, padding):
    image_padded = np.pad(image, ((padding, padding), (padding, padding), (0, 0)), mode='constant',
                        constant_values=0)
    return image_padded

def LoadImage(path, size = None):
    image = plot.imread(path).copy()
    if not size is None:
        image = resize(image, output_shape = size)

    image = np.swapaxes(image, 0, 2)
    image[0] = np.flip(image, 0)
    return image


def ProgressBar(percent, num = 15):
    done_chars = int(min(max(percent, 0), 1) * num)
    left_chars = num - done_chars
    return '|' + chr(9608) * done_chars + ' ' * left_chars + '|'