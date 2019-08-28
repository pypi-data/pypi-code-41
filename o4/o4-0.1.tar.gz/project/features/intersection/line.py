import cv2

from features.util.text import Text
from features.feature import Feature
from project.utils import percentage_location


class Line(Feature):
  def __init__(self, start_point, end_point, color=(0, 0, 255), thickness=2, positive_text=None, negative_text=None,
               percentage_location=False):
    super().__init__()

    self.start_point = start_point
    self.end_point = end_point
    self.color = color
    self.thickness = thickness

    self.percentage_location = percentage_location

    self.positive_text = positive_text
    self.negative_text = negative_text

    # stats
    self.positives = 0
    self.negatives = 0

  def set_o4(self, o4):
    if self.percentage_location:
      self.start_point = percentage_location(self.start_point, o4)
      self.end_point = percentage_location(self.end_point, o4)

      if self.positive_text is None:
        x = int(self.start_point[0] + 0.05 * o4.WIDTH)
        y = int(self.start_point[1] - 0.12 * self.start_point[1])
        self.positive_text = Text((x, y), text="Up: ", color=(0, 0, 255),font_size=20)
        self.positive_text.set_o4(o4)

      if self.negative_text is None:
        x = int(self.start_point[0] + 0.05 * o4.WIDTH)
        y = int(self.start_point[1] + 0.02 * self.start_point[1])
        self.negative_text = Text((x, y), text="Down: ", color=(0, 0, 255),font_size=20)
        self.negative_text.set_o4(o4)

      # y=ax+b
      self.slope = (self.end_point[1] - self.start_point[1]) / (self.end_point[0] - self.start_point[0])
      self.b = self.start_point[1] - 1 * self.slope * self.start_point[0]

  def perform(self, o4, frame, detections, time_unit):
    for detection in detections:
      if len(detection.history_location) < 2:
        continue

      in_positive = self.in_positive_area(detection.center)
      if in_positive != self.in_positive_area(detection.history_location[-2]):
        if in_positive:
          self.negatives += 1
        else:
          self.positives += 1

    self.history.add(time_unit, [self.positives, self.negatives])
    return (self.positives, self.negatives)

  def _draw(self, o4, frame, detections, time_unit):
    # line
    cv2.line(frame, self.start_point, self.end_point, self.color, self.thickness)

    self.positive_text.draw(frame, str(self.positives))
    self.negative_text.draw(frame, str(self.negatives))
    return frame

  def draw(self, o4, draw, detections, time_unit):
    # line
    draw.line([self.start_point, self.end_point], fill='blue')

    self.positive_text.draw(draw, str(self.positives))
    self.negative_text.draw(draw, str(self.negatives))
    return draw

  def in_positive_area(self, point):
    return point[1] >= self.slope * point[0] + self.b
