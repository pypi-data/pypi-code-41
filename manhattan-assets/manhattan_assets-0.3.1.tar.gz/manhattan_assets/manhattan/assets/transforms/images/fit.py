
from manhattan.assets.transforms.base import BaseTransform

__all__ = ['Fit']


class Fit(BaseTransform):
    """
    Resize an image to fit within a set of dimensions. The width and height
    should be specified in pixels.
    """

    _id = 'image.fit'

    def __init__(self, width, height=None):
        super().__init__({'width': width, 'height': height or width})

