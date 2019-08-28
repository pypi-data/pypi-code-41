import numpy as np
import cv2

from detection.detectors.detector import Detector
from detection.detectors.yolo3_opencv import config

from o4.point import Point


class DnnYoloDetector(Detector):

  def __init__(self, confidence=0.5, threshold=0.2, min_box_size=0):
    # yolo settings
    self.CONFIDENCE_VALUE = confidence
    self.THRESHOLD_VALUE = threshold
    self.net, self.ln, self.LABELS = config.load_model()

    self.min_box_size = min_box_size
    self.set_label_colors()

  def detect(self, frame, W, H, time_unit):

    # construct a blob from the input frame and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes
    # and associated probabilities
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    self.net.setInput(blob)
    layerOutputs = self.net.forward(self.ln)

    # initialize our lists of detected bounding boxes, confidences,
    # and class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
      # loop over each of the detections
      for detection in output:
        # extract the class ID and confidence (i.e., probability)
        # of the current object detection
        scores = detection[5:]
        classID = np.argmax(scores)
        confidence = scores[classID]

        # filter out weak predictions by ensuring the detected
        # probability is greater than the minimum probability
        if confidence > self.CONFIDENCE_VALUE:

          # scale the bounding box coordinates back relative to
          # the size of the image, keeping in mind that YOLO
          # actually returns the center (x, y)-coordinates of
          # the bounding box followed by the boxes' width and
          # height
          box = detection[0:4] * np.array([W, H, W, H])
          (centerX, centerY, width, height) = box.astype("int")

          # accept only detections with a min size (width or size)
          if not self.assert_box_size(width, height):
            continue

          predicted_class = self.LABELS[classID]
          if predicted_class in self.not_detect:
            continue

          # use the center (x, y)-coordinates to derive the top
          # and and left corner of the bounding box
          x = int(centerX - (width / 2))
          y = int(centerY - (height / 2))

          # update our list of bounding box coordinates,
          # confidences, and class IDs
          boxes.append([x, y, int(width), int(height)])
          confidences.append(float(confidence))
          classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping
    # bounding boxes
    # idxs = cv2.dnn.NMSBoxes(boxes, confidences, confidence,
    #                        self.THRESHOLD_VALUE)

    idxs = self.supress_detections(boxes, confidences, confidence=confidence, threshold=self.THRESHOLD_VALUE)

    detections = []
    if len(idxs) > 0:
      for i in idxs.flatten():
        box = boxes[i]
        point = Point((box[0], box[1]), (box[0] + box[2], box[1] + box[3]), box[2], box[3],
                      self.LABELS[classIDs[i]],
                      confidences[i],
                      time_unit, frame)
        detections.append(point)

    return detections
