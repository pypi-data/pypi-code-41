# -*- coding: utf-8 -*-
import cv2
import numpy as np
from PIL import Image
import re
from thumbor.filters import BaseFilter, filter_method
from thumbor_extras.filters import rainbow

class Filter(BaseFilter):
    @filter_method(
        BaseFilter.PositiveNonZeroNumber,
        BaseFilter.Boolean,
        BaseFilter.Boolean,
        BaseFilter.Boolean,
        BaseFilter.PositiveNumber,
        BaseFilter.PositiveNumber,
        BaseFilter.PositiveNumber
    )
    def draw_focal_points(self, line_width=3, show_heatmap=True, show_labels=True, show_rainbow=True, r=0, g=255, b=0):
        img = np.array(self.engine.image)
        class_label_regex = re.compile('DNN Object Detection \(class: ([a-z ]+)\)')
        for index, focal_point in enumerate(self.context.request.focal_points):
            width = int(focal_point.width)
            height = int(focal_point.height)
            left = int(focal_point.x - (width / 2))
            top = int(focal_point.y - (height / 2))
            right = left + width
            bottom = top + height
            weight = focal_point.weight

            # 🌈-map
            if show_rainbow:
                color = rainbow[index % len(rainbow)]
                r, g, b = color

            # A 🔥 heatmap 🔥 (kinda) from transparent (0% confidence) to opaque (100% confidence)
            if show_heatmap:
                overlay = img.copy()
                cv2.rectangle(overlay, (left, top), (right, bottom), (r, g, b), line_width)
                cv2.addWeighted(overlay, weight, img, 1 - weight, 0, img)
            else:
                cv2.rectangle(img, (left, top), (right, bottom), (r, g, b), line_width)

            # Draw class labels
            match = class_label_regex.match(focal_point.origin)
            if show_labels and match:
                # one-tenth the height of the box
                label_height = height / 10
                # the font is *about* 30 pixels tall
                scale = label_height / 30.
                class_label = match.groups(1)[0]
                cv2.putText(
                    img,
                    ' {} ({:0.3f})'.format(class_label, weight),
                    (left, top + label_height),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    scale,
                    (r, g, b),
                    line_width
                )

            self.engine.image = Image.fromarray(img)
