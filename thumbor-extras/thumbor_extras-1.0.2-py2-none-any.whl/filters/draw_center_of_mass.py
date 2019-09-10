import cv2
import numpy as np
from PIL import Image
from thumbor.filters import BaseFilter, filter_method

class Filter(BaseFilter):
    @filter_method(
        BaseFilter.PositiveNumber,
        BaseFilter.PositiveNumber,
        BaseFilter.PositiveNumber
    )
    def draw_center_of_mass(self, r=255, g=0, b=0):
        x, y = self.context.transformer.get_center_of_mass()
        img = np.array(self.engine.image)
        # draw by percentage of height
        size_pct = 0.05
        radius = int(img.shape[1] * size_pct / 2)
        cv2.circle(img, (int(x), int(y)), radius, (r, g, b), -1)
        self.engine.image = Image.fromarray(img)
