from numpy.ma.bench import timer

from features.feature import Feature
from features.util.text import Text
from timeit import default_timer as timer


class FPS(Feature):
  def __init__(self, text_feature=None):
    super().__init__()

    self.accum_time = 0
    self.curr_fps = 0
    self.prev_time = timer()
    self.fps= self.fps_to_show = 0

    if text_feature is None:
      self.text_feature = Text((0.03, 0.8), text="FPS: ", color=(0, 0, 255), percentage_location=True)
    else:
      self.text_feature = text_feature

  def set_o4(self, o4):
    self.text_feature.set_o4(o4)

  def perform(self, o4, frame, detections, time_unit):
    curr_time = timer()
    exec_time = curr_time - self.prev_time

    self.prev_time = curr_time
    self.accum_time = self.accum_time + exec_time
    self.curr_fps = self.curr_fps + 1

    if self.accum_time > 1:
      self.accum_time = self.accum_time - 1
      self.fps_to_show = self.fps = self.curr_fps
      self.curr_fps = 0

    return self.fps

  def draw(self, o4, frame, detections, time_unit):
    self.text_feature.draw(frame, str(self.fps_to_show))

    return frame
