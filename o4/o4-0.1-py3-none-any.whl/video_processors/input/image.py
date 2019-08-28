import cv2

from .video_processor import VideoProcessor


class Image(VideoProcessor):

  def __init__(self, directory):
    self.image = cv2.imread(directory)
    self.time_unit = 0

  def get_frame(self):
    return True, self.image, self.time_unit
