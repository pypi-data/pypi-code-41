import numpy as np
import cv2


class Detector():
  def detect(self, frame, W, H, time_unit):
    pass

  def set_not_detect(self, not_detect):
    self.not_detect = not_detect

  def get_colors(self):
    return self.COLORS

  def get_labels(self):
    return self.LABELS

  def set_label_colors(self):
    # initialize a list of colors to represent each possible class label
    np.random.seed(42)
    random_colors = np.random.randint(0, 255, size=(len(self.LABELS), 3),
                                      dtype="uint8")
    self.COLORS = {}
    for i, label in enumerate(self.LABELS):
      self.COLORS[label] = random_colors[i]

  def set_min_box_size(self, size):
    self.min_box_size = size

  def set_max_box_size(self, size):
    self.max_box_size = size

  def assert_box_size(self, width, height):
    size = width + height
    return (size >= self.min_box_size) and (size <= self.max_box_size)

  def supress_detections(self, boxes, confidences, confidence=0.5, threshold=0.1):
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confidence,
                            threshold)
    return idxs

  def not_overlap(self, point, detections, supress_iou_over=0.05):
    areaNew = point.width * point.height

    for i, p in enumerate(detections):
      # never overlap
      if p.right_bottom[1] <= point.left_top[1] or point.right_bottom[1] <= p.left_top[1] or (p.right_bottom[0] <= point.left_top[0])or (point.right_bottom[0] <= p.left_top[0]):
        continue

      if p.left_top[1] > point.left_top[1]:
        top = p.left_top[1]
      else:
        top = point.left_top[1]

      if p.right_bottom[1] < point.right_bottom[1]:
        bottom = p.right_bottom[1]
      else:
        bottom = point.right_bottom[1]

      if p.left_top[0] > point.left_top[0]:
        left = p.left_top[0]
      else:
        left = point.left_top[0]

      if p.right_bottom[0] < point.right_bottom[0]:
        right = p.right_bottom[0]
      else:
        right = point.right_bottom[0]

      intersection = (bottom - top) * (right - left)

      areaOld = p.width * p.height
      union = areaNew + areaOld - intersection

      #print("----------BEGIN----------")
      #print(p.left_top,p.right_bottom)
      #print(point.left_top, point.right_bottom)
      #print(left,top,right,bottom)
      #print(bottom - top)
      #print(right - left)
      #print(intersection)
      #print(intersection / union)
      #print("----------END------------")

      if intersection / union >= supress_iou_over:

        if p.confidence > point.confidence:
          return False
        else:
          del detections[i]
          return True

    return True
