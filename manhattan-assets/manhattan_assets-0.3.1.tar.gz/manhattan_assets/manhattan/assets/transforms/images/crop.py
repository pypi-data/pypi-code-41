
from manhattan.assets.transforms.base import BaseTransform

__all__ = ['Crop']


class Crop(BaseTransform):
    """
    Apply a crop to an image.

    Each value (top, left, bottom, right) should be between 0.0 and 1.0
    representing a normalized value for the given dimension.
    """

    _id = 'image.crop'

    def __init__(self, top, left, bottom, right):
        super().__init__({
            'top': top,
            'left': left,
            'bottom': bottom,
            'right': right
        })
