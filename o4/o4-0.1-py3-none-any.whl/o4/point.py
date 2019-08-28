from o4 import settings
from project.tracking.kalman import kalman_xy
import numpy as np
from fingerprint import color_histogram as ch
from project.utils import geometry

R = 15
P = np.matrix(np.eye(4)) * 1000  # initial uncertainty


class Point():
  def __init__(self, left_top, right_bottom, width, height, className, confidence, time_unit, frame):
    self.center = (left_top[0] + int((right_bottom[0] - left_top[0]) / 2), right_bottom[1])

    self.left_top = left_top
    self.right_bottom = right_bottom

    self.width = width
    self.height = height

    self.width_history = []
    self.height_history = []

    self.className = className
    self.confidence = confidence
    self.last_time_unit = time_unit

    self.color_hist = ch.region_color_histogram(frame, left_top, right_bottom)

  def accept(self, id, classId):
    self.id = id
    self.classId = classId

    self.history_location = []
    self.prediction_location = []

    x = np.matrix([self.center[0], self.center[1], 0.0, 0.0]).T
    self.prediction_model, self.uncertainty = kalman_xy(x, P, self.center, R)

    self.speed_vector = self.prediction_model[2:4]

    self.speed = 0
    self.speed_history = []

  def set_id(self, id):
    self.id = id

  def predict(self, time_unit):
    time_dif = time_unit - self.last_time_unit

    x, y = self.center

    x += int(self.speed_vector[0] * time_dif)
    y += int(self.speed_vector[1] * time_dif)

    return (x, y)

  def measurement(self, measured_point):
    self.last_time_unit = measured_point.last_time_unit

    self.set_box(measured_point.left_top, measured_point.right_bottom)

    self.history_location.append(self.center)
    self.set_speed()

    self.className = measured_point.className
    self.confidence = measured_point.confidence

    # tracking
    self.prediction_location = [self.predict(self.last_time_unit + x) for x in range(25)]
    self.prediction_model, self.uncertainty = kalman_xy(self.prediction_model, self.uncertainty, self.center, R)
    self.speed_vector = [self.prediction_model[2] / settings.DETECTOR_ON_N_FRAME,
                         self.prediction_model[3] / settings.DETECTOR_ON_N_FRAME]

    # fingerprint
    self.color_hist = measured_point.color_hist

  def predict_measurement(self, time_unit):

    prediction = self.predict(time_unit)
    self.last_time_unit = time_unit

    self.set_box(prediction=prediction)
    self.history_location.append(self.center)

    # tracking
    self.prediction_location = [self.predict(self.last_time_unit + x) for x in range(25)]

  def __str__(self):
    return str(self.id)

  def set_box(self, left_top=None, right_bottom=None, prediction=None):

    if prediction:
      self.center = prediction
      self.left_top = prediction[0] - int(self.width / 2), prediction[1] + self.height
      self.right_bottom = prediction[0] + int(self.width / 2), prediction[1]
      return

    width = right_bottom[0] - left_top[0]
    height = left_top[1] - right_bottom[1]
    self.width_history.append(width)
    self.height_history.append(height)

    if len(self.width_history) > 5:
      self.width = sum(self.width_history[-5:]) / 5
      self.height = sum(self.height_history[-5:]) / 5
    else:
      self.width = sum(self.width_history) / len(self.width_history)
      self.height = sum(self.height_history) / len(self.width_history)

    self.width_history[-1] = (self.width)
    self.height_history[-1] = (self.height)

    width_diff = int((self.width - width) / 2)
    height_diff = int((self.height - height) / 2)

    self.left_top = left_top[0] - width_diff, left_top[1] - height_diff
    self.right_bottom = right_bottom[0] - width_diff, right_bottom[1] - height_diff

    self.center = (self.right_bottom[0] - int(self.width / 2), self.right_bottom[1])

  def set_speed(self):
    x, y = self.center
    lenHist = len(self.history_location)
    if lenHist > 2:
      last_point = self.history_location[-2]
      self.speed_vector = (x - last_point[0]), (y - last_point[-1])
      self.speed = geometry.distance(self.center, last_point)

    '''
    if lenHist > 10:
      lastx, lasty = self.history_location[-10]
      self.speed_vector = (x - lastx) / 10, (y - lasty) / 10
      self.speed = geometry.distance(self.center, (lastx, lasty))/10

    else:
      lastx, lasty = self.history_location[-lenHist]
      self.speed_vector = (x - lastx) / lenHist, (y - lasty) / lenHist
      self.speed = geometry.distance(self.center, (lastx, lasty))/lenHist
    '''
    self.speed_history.append(self.speed)
