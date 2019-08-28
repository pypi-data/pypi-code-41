import cv2

from features.feature import Feature
from project.utils import sigmoid
from project.utils import distance
import numpy as np


class Heatmap(Feature):
  def __init__(self):
    super().__init__()
    self.radious = 8

  def perform(self, o4, frame, detections, time_unit):
    pass

  def draw(self, o4, frame, detections, time_unit):

    all_dots = []
    for object in o4.get_objects():
      all_dots.extend(object.history_location)

    return self._heatmap(frame, all_dots)

  def show(self, img):
    self.draw()
    pass

  def heatmap(self, frame, o4):
    all_dots = []
    for object in o4.get_objects():
      all_dots.extend(object.history_location)

    dots, dots_occurence = self.dots_occurence(all_dots)
    heatmap_img = self.colormap(dots, dots_occurence, frame.shape)
    frame = cv2.addWeighted(frame, 0.5, heatmap_img, 0.5, 0)

    return frame

  def _heatmap(self, frame, all_dots):
    dots, dots_occurence = self.dots_occurence(all_dots)
    heatmap_img = self.colormap(dots, dots_occurence, frame.shape)
    frame = cv2.addWeighted(frame, 0.5, heatmap_img, 0.5, 0)

    return frame

  def dots_occurence(self, all_dots):
    dots = []
    occurrences = []
    while len(all_dots) > 0:
      dot = all_dots.pop(0)
      n = 1
      for d in all_dots:
        if distance(dot, d) <= self.radious:
          n += 1
          del d

      dots.append(dot)
      occurrences.append(n)
    return dots, occurrences

  def colormap(self, dots, dots_occurence, shape):
    maxValue = max(dots_occurence)
    dots_occurence = list(map(lambda x: int(sigmoid(x / maxValue) * 255), dots_occurence))

    matrix = np.zeros((shape[0], shape[1]), dtype=np.uint8)

    sortedIdx = [i[0] for i in sorted(enumerate(dots_occurence), key=lambda x: x[1])]
    for i in sortedIdx:
      cv2.circle(matrix, dots[i], self.radious, dots_occurence[i], -1)

    return cv2.applyColorMap(matrix, cv2.COLORMAP_JET)
