import cv2

from features import Text
from features.feature import Feature


class AreaCounter(Feature):
  def __init__(self, upper_left, bottom_right, text_feature=None, object_types=[], color=(0, 255, 0)):
    super().__init__()

    self.object_types = object_types

    if text_feature is None:
      self.text_feature = Text((upper_left[0], upper_left[1] - 5), text="Inside: ", color=(0, 255, 0))
    else:
      self.text_feature = text_feature

    self.upper_left = upper_left
    self.bottom_right = bottom_right
    self.color = color
    self.colorTransparent = (int(color[0]), int(color[1]),
                      int(color[2]), 75)
    self.counter = 0

  def set_o4(self, o4):
    self.object_types_ids = [o4.get_object_id(o) for o in self.object_types]
    self.text_feature.set_o4(o4)

  def perform(self, o4, frame, detections, time_unit):

    counter = 0
    for detection in detections:
      x, y = detection.center
      if x >= self.upper_left[0] and x <= self.bottom_right[0] and y >= self.upper_left[1] and y <= self.bottom_right[
        1]:
        counter += 1

    self.counter = counter
    self.history.add(time_unit, counter)
    return counter

  def _draw(self, o4, frame, detections, time_unit):
    # area
    cv2.rectangle(frame, self.upper_left, self.bottom_right, self.color, 1)
    self.text_feature.draw(frame, str(self.counter))
    return frame

  def draw(self, o4, draw, detections, time_unit):
    # area
    draw.rectangle([self.upper_left, self.bottom_right], fill=self.colorTransparent)
    self.text_feature.draw(draw, str(self.counter))
    return draw
