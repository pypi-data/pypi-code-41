from features.util.text import Text
from features.feature import Feature


class Counter(Feature):
  def __init__(self, all=True, continuous=False, object_types=[], text_feature=None):
    super().__init__()

    self.all = all
    if len(object_types) > 0:
      self.all = False

    self.object_types = object_types

    if text_feature is None:
      self.text_feature = Text((20, 50), text="Counter: ", color=(0, 0, 0))
    else:
      self.text_feature = text_feature

    self.counter = 0

  def set_o4(self, o4):
    self.text_feature.set_o4(o4)

  def perform(self, o4, frame, detections, time_unit):
    if self.all:
      return o4.get_unique_objects()

    counter = 0
    for detection in detections:
      if detection.className in self.object_types:
        counter += 1

    self.history.add(time_unit, counter)
    self.counter = counter
    return counter

  def draw(self, o4, frame, detections, time_unit):
    self.text_feature.draw(frame, str(self.counter))
    return frame

  def serialize(self):
    return {"value": self.counter}
