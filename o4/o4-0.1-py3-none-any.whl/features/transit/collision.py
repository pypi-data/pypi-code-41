from __future__ import division

from features.util.text import Text
from features.feature import Feature
import math
from project.utils import geometry, stats


class Collision(Feature):
  def __init__(self, all=True, object_types=['car', 'truck', 'bus'], text_feature=None, time_units_to_collision=10):
    super().__init__()

    self.all = all
    if len(object_types) > 0:
      self.all = False

    self.object_types = object_types

    if text_feature is None:
      self.text_feature = Text((20, 50), text="State: ", color=(0, 0, 0))
    else:
      self.text_feature = text_feature

    self.states = ['SECURE', 'DANGER', 'COLLISION']
    self.collision_state = self.states[0]
    self.collided_history = []
    self.stack_collided = []
    self.states_history = [0 for x in range(10)]

    self.threshold_speed_diff = 2

    self.time_units_to_collision = time_units_to_collision

  def set_o4(self, o4):
    self.text_feature.set_o4(o4)

  def perform(self, o4, frame, detections, time_unit):
    self.collision_state = 0
    states = [0]
    collision_data = self.collision_data(detections)
    for i in range(0, len(collision_data) - 1):
      for j in range(i + 1, len(collision_data)):
        intersection = self.intersection(collision_data[i]['line'], collision_data[j]['line'])

        if intersection:
          distance = geometry.distance(intersection, collision_data[i]['edgePoint'])

          timeStepsToCollision = distance / collision_data[i]['advanceByTimeUnit']

          if collision_data[i]['collision']:
            states.append(2)
            print("STATE COLLISION")
          elif timeStepsToCollision < 30:
            states.append(1)
          else:
            states.append(0)

    self.states_history.append(max(states))
    self.collision_state = max(self.states_history)
    self.states_history.pop(0)
    print(self.states[self.collision_state])

    return self.collision_state

  def draw(self, o4, draw, detections, time_unit):
    self.text_feature.draw(draw, str(self.states[self.collision_state]))
    for line in self.lines:
      draw.line(line, fill='red')
    return draw

  def serialize(self):
    return {"value": self.collision_state}

  def collision_data(self, detections):

    collisionData = []
    self.lines = []
    for detection in detections:

      predition = detection.prediction_location
      if not predition:
        continue
      self.lines.append(predition)
      collisionItem = {}

      center = detection.center
      angle = math.degrees(math.atan2(predition[-1][1] - predition[0][1], predition[-1][0] - predition[0][0]))
      if angle < 0:
        angle += 360

      if angle > 315 or angle < 45:
        # rigth
        edge_point = (center[0] + detection.width / 2, center[1] + detection.height / 2)
        predition = list(
          map(lambda x: (x[0] + detection.width / 2, x[1] + detection.height / 2), detection.prediction_location))
      elif angle > 225:
        # bottom
        edge_point = center
      elif angle > 135:
        # left
        edge_point = (center[0] - detection.width / 2, center[1] + detection.height / 2)
        predition = list(map(lambda x: (x[0], x[1] + detection.height), detection.prediction_location))
      else:
        # top
        edge_point = (center[0], center[1] + detection.height)
        predition = list(map(lambda x: (x[0] - detection.width / 2, x[1]), detection.prediction_location))

      collisionItem['detection'] = detection
      collisionItem['edgePoint'] = edge_point
      collisionItem['prediction'] = predition
      collisionItem['line'] = self.line(predition[0], predition[-1])
      advanceByTimeUnit = max(geometry.distance(predition[0], predition[1]), 0.001)
      collisionItem['advanceByTimeUnit'] = advanceByTimeUnit

      speed_history = detection.speed_history
      if len(speed_history) > 40:
        mean_previous_history = sum(speed_history[-50:-10]) / 40
        stdv = stats.stddev(speed_history[-50:-10])

        mean_recent_history = sum(speed_history[-10:]) / 10

        collision = abs(mean_recent_history - mean_previous_history) > stdv * self.threshold_speed_diff
        if collision:
          print("Dif: {:.2f}\nThreshold: {:.2f} \n\n".format(abs(mean_recent_history - mean_previous_history),
                                                             stdv * self.threshold_speed_diff))
      else:
        collision = False

      collisionItem['collision'] = collision

      collisionData.append(collisionItem)

    return collisionData

  def line(self, p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0] * p2[1] - p2[0] * p1[1])
    return A, B, -C

  def intersection(self, L1, L2):
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
      x = Dx / D
      y = Dy / D
      return x, y
    else:
      return False
