from .history.history import History


class Feature():

  def __init__(self, broadcast=False):
    self.history = History()
    self.broadcast = broadcast

  def set_o4(self, o4):
    self.o4 = o4

  def perform(self, o4, frame, detections, time_unit):
    pass

  def draw(self, o4, frame, detections, time_unit):
    return frame

  def serialize(self):
    pass

  def broadcast_as(self, name):
    self.broadcast = True
    self.broadcast_name = name
