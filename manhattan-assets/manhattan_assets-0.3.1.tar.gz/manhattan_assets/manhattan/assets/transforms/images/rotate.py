
from manhattan.assets.transforms.base import BaseTransform

__all__ = ['Rotate']


class Rotate(BaseTransform):
    """
    Rotate an image by 90, 180 or 270 degrees.
    """

    _id = 'image.rotate'

    def __init__(self, angle):
        super().__init__({'angle': angle})
