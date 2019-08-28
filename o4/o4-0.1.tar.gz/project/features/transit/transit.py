from features import Text
from features.feature import Feature
import numpy as np


class Transit(Feature):
  def __init__(self, threshold_states=[0, 10, 30], text_feature=None):
    super().__init__()
    self.object_types = ['car', 'truck', 'bus']

    if text_feature is None:
      self.text_feature = Text((0.4, 0.1), text="Transit: ", percentage_location=True)
    else:
      self.text_feature = text_feature

    self.states = ['EMPTY', 'LOW', 'MEDIUM', 'HIGH']
    self.threshold_states = threshold_states
    self.state = self.states[0]

  def perform(self, o4, frame, detections, time_unit):
    counter = 0

    for detection in detections:
      if detection.className in self.object_types:
        counter += 1

    atribution = False
    for i, threshold in enumerate(self.threshold_states):
      if counter <= threshold:
        atribution = True
        self.state = self.states[i]
        break

    if not atribution:
      self.state = self.states[-1]

    return self.state

  def draw(self, o4, draw, detections, time_unit):
    self.text_feature.draw(draw, self.state)
    return draw
