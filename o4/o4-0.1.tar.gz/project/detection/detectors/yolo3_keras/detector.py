from detection.detectors.detector import Detector

from detection.detectors.yolo3_keras import yolo
from o4.point import Point
import numpy as np
from PIL import Image


class YoloKerasDetector(Detector):
  def __init__(self, confidence=0.3, threshold=0.3, min_box_size=20, gpu=False, not_detect=[]):
    self.min_box_size = min_box_size
    self.yolo = yolo.YOLO()
    self.LABELS = self.yolo.class_names
    self.set_label_colors()

    self.not_detect = not_detect

  def detect(self, frame, W, H, time_unit):
    image = Image.fromarray(frame)
    out_boxes, out_scores, out_classes = self.yolo.detect_image(image)

    detections = []
    #print("\nframe: {}".format(time_unit))
    for i, c in reversed(list(enumerate(out_classes))):

      top, left, bottom, right = out_boxes[i]

      score = out_scores[i]

      top = max(0, np.floor(top + 0.5).astype('int32'))
      left = max(0, np.floor(left + 0.5).astype('int32'))
      bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
      right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

      width = right - left
      height = bottom - top

      if not self.assert_box_size(width, height):
        continue

      predicted_class = self.LABELS[c]
      if predicted_class in self.not_detect:
        continue
      point = Point((left, top), (right, bottom),width,height, predicted_class, score, time_unit, frame)

      if self.not_overlap(point, detections):
        detections.append(point)

    return detections
