from features.feature import Feature
from features.util.text import Text


class FrameCounter(Feature):
  def __init__(self, text_feature=None):
    super().__init__()

    self.counter = 0

    if text_feature is None:
      self.text_feature = Text((0.03, 0.9), text="Frame: ", color=(0, 0, 255), percentage_location=True)
    else:
      self.text_feature = text_feature

  def set_o4(self, o4):
    self.text_feature.set_o4(o4)

  def perform(self, o4, frame, detections, time_unit):
    self.counter += 1
    return self.counter

  def draw(self, o4, frame, detections, time_unit):
    self.text_feature.draw(frame, str(self.counter))
    return frame
