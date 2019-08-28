import math
from munkres import Munkres

from fingerprint import color_histogram as ch


class Tracking():

  def __init__(self):
    self.idCounter = 0
    self.idByClassName = {}

    self.points = []
    self.hungarian = Munkres()
    self.save_point_by_time = 100

    self.not_equal_comparison_threshold = 100
    self.not_equal_fingerprint_threshold = 0.7
    self.not_equal_distance_threshold = 0.1

    # debug
    self.stats = {}

  def setup(self, o4):
    for name in o4.detection.get_labels():
      self.idByClassName[name] = 0

    self.not_equal_distance_threshold = o4.WIDTH * self.not_equal_distance_threshold

  def measurement(self, frame, measured_points, time_unit):

    # exclude points detected long time ago
    self.points = list(filter(lambda x: x.last_time_unit > time_unit - self.save_point_by_time, self.points))
    if len(measured_points) == 0:
      return []

    if not self.points:
      self.add_initials(measured_points)

    # predicted positions of points
    predictedPoints = self.predict(time_unit)

    assignmentMatrix = []

    # matrix construction rows predicted, columns measurements
    for p, predicted in predictedPoints:
      row = []
      for measured in measured_points:
        row.append(self._comparison(measured, p, predicted))
      assignmentMatrix.append(row)

    # matching of detected points with previous points
    indexes = self.hungarian.compute(assignmentMatrix)

    for row, column in indexes:
      if assignmentMatrix[row][column] >= self.not_equal_comparison_threshold:
        continue
      # print("{} : {}".format(self.points[row].id, assignmentMatrix[row][column]))
      if self.points[row].id in self.stats:
        self.stats[self.points[row].id].append(assignmentMatrix[row][column])
      else:
        self.stats[self.points[row].id] = [assignmentMatrix[row][column]]

      self.points[row].measurement(measured_points[column])
      measured_points[column] = None

    # add points that were not matched with existing points to the list of unique points
    self.add_initials(measured_points)

    return list(filter(lambda x: x.last_time_unit == time_unit, self.points))

  def predict_measurements(self, time_unit):
    # exclude points detected long time ago
    self.points = list(filter(lambda x: x.last_time_unit > time_unit - self.save_point_by_time, self.points))

    for point in self.points:
      point.predict_measurement(time_unit)

    return list(filter(lambda x: x.last_time_unit == time_unit, self.points))

  def add_initials(self, measured_points):
    for measured in measured_points:
      if not measured is None:
        self._add_initial(measured)

  def predict(self, time_unit):
    return [(p, p.predict(time_unit)) for p in self.points]

  def _add_initial(self, measured):
    self.idCounter += 1

    classId = self.idByClassName[measured.className] + 1
    self.idByClassName[measured.className] = classId

    measured.accept(self.idCounter, classId)
    self.points.append(measured)

  def _distance(self, a, b):

    return math.sqrt(math.pow(b[0] - a[0],2) + math.pow(b[1] - a[1],2))

  def _comparison(self, measured, point, predicted):
    color_comparison = ch.region_hist_compare(measured.color_hist, point.color_hist)

    if color_comparison > self.not_equal_fingerprint_threshold:
      return self.not_equal_comparison_threshold
    try:
      distance = self._distance(measured.center, predicted)
    except:
      print(measured.center)
      print(predicted)
      raise ValueError('A very specific bad thing happened.')

    if distance > self.not_equal_distance_threshold:
      return self.not_equal_comparison_threshold

    comparison = color_comparison * distance
    return comparison
