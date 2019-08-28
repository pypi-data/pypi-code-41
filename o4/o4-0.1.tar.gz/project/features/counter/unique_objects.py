from features.util.text import Text
from features.feature import Feature


class UniqueObjects(Feature):
  def __init__(self, object_types=[], all=False, text_feature=None, text="Unique objects: "):
    super().__init__()
    self.counter = 0
    self.object_types = object_types

    self.all = all

    if text_feature is None:
      self.text_feature = Text((0.03, 0.05), text=text, color=(0, 0, 0), percentage_location=True)
    else:
      self.text_feature = text_feature

  def set_o4(self, o4):
    self.text_feature.set_o4(o4)

  def perform(self, o4, frame, detections, time_unit):
    self.counter = o4.get_unique_objects(classNames=self.object_types, all=self.all)

    self.history.add(time_unit, [self.counter])

  def draw(self, o4, frame, detections, time_unit):
    self.text_feature.draw(frame, str(self.counter))
    return frame

  def serialize(self):
    return {"counter": self.counter}
