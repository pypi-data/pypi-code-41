from features.feature import Feature
from project.utils import percentage_location
from PIL import ImageFont


class Text(Feature):
  def __init__(self, location, text="", color=(0, 0, 0),font_size=50, percentage_location=False):
    self.location = location
    self.text = text
    self.color = color
    self.data = ""
    self.percentage_location = percentage_location

    self.font_size = font_size
    self.font = ImageFont.truetype("arial", size=self.font_size)

  def set_o4(self, o4):
    if self.percentage_location:
      self.location = percentage_location(self.location, o4)

  def _draw(self, frame, data):
    text = self.text + data
    # cv2.putText(frame, text, self.location,
    #            self.font, 0.5, self.color, 1)
    return frame

  def draw(self, draw, data):
    data = self.text + data

    x, y = self.location

    draw.rectangle([(x - 8, y), (x + 8 + len(data) * self.font_size/2.0, y + self.font_size/0.8)], fill='black')
    draw.text((x, y), data, font=self.font)

    return draw
