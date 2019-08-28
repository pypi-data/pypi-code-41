import cv2

from features.feature import Feature

import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


class DetectionBoxes(Feature):
  def __init__(self, show_history=True, show_prediction=False, thickness=2, mask=True, label=True):
    super().__init__()
    self.show_prediction = show_prediction
    self.show_history = show_history
    self.label = label

    self.thickness = thickness
    self.mask = mask

    self.font_size = 25
    self.font = ImageFont.truetype("arial", size=self.font_size)

  def _draw(self, o4, frame, detections, time_unit):
    colors = o4.get_colors()
    historyLines = []
    predictionLines = []

    for detected in detections:
      # extract the bounding box coordinates
      (x, y) = detected.left_top

      # draw a bounding box rectangle and label on the frame
      color = [int(c) for c in colors[detected.className]]
      cv2.rectangle(frame, (x, y), detected.right_bottom, color, self.thickness)

      # label
      if self.label:
        text = "{} {}".format(detected.id, detected.className)
      else:
        text = str(detected.id)

      cv2.rectangle(frame, (x - 1, y - 22), (x + 6 + len(text) * 10, y), color, -1)
      cv2.putText(frame, text, (x + 3, y - 5),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

      # draw center of box
      cv2.circle(frame, detected.center, 2, (0, 0, 255), -1)

      if self.show_history:
        historyLines.append(np.array(detected.history_location[-10:]))

      if self.show_prediction:
        predictionLines.append(np.array(detected.prediction_location))

    cv2.polylines(frame, historyLines, False, (0, 0, 255), 1)
    cv2.polylines(frame, predictionLines, False, (0, 255, 255), 1)
    return frame

  def draw(self, o4, draw, detections, time_unit):

    colors = o4.get_colors()


    for detected in detections:
      # extract the bounding box coordinates
      (x, y) = detected.left_top

      # draw a bounding box rectangle and label on the frame
      colorDefault = [int(colors[detected.className][0]), int(colors[detected.className][1]),
                      int(colors[detected.className][2]), 255]
      color = tuple(colorDefault)

      colorDefault[3] = 100
      tranparentColor = tuple(colorDefault)

      draw.rectangle([(x, y), detected.right_bottom], fill=tranparentColor)
      draw.rectangle([(x, y), detected.right_bottom], outline=color, width=2)

      # label
      if self.label:
        text = "{} {}".format(detected.id, detected.className)
      else:
        text = str(detected.id)

      draw.rectangle([(x - 1, y - 25), (x + 5 + len(text) * 15, y)], fill=color)
      draw.text((x + 3, y - 25), text, font=self.font, fill='black')

      # draw center of box
      draw.ellipse((detected.center[0] - 2, detected.center[1] - 2, detected.center[0] + 2, detected.center[1] + 2),
                   fill='blue', outline='blue')

      if self.show_history:
        historyLines = detected.history_location[-10:]
        if len(historyLines) > 1:
          draw.line(historyLines, fill='blue')

      if self.show_prediction:
        predictionLines = detected.prediction_location[:10]
        if len(predictionLines) > 1:
          draw.line(predictionLines, fill='green')

    return draw
