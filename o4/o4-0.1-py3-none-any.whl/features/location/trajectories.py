import cv2

from features.feature import Feature
import numpy as np


class Trajectories(Feature):
  def __init__(self):
    super().__init__()
    self.lines = []

  def perform(self, o4, frame, detections, time_unit):
    self.lines = []
    for object in o4.get_objects():
      self.lines.append(np.array(object.history_location))

    return self.lines

  def draw(self, o4, frame, detections, time_unit):

    cv2.polylines(frame, self.lines, False, (28, 28, 183), 1)
    return frame
