import cv2

from .video_processor import VideoProcessor


class IPCam(VideoProcessor):

  def __init__(self, url):

    self.cam = cv2.VideoCapture(url)
    self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 0)
    self.time_unit = 0

  def get_frame(self):
    self.time_unit += 1
    grabbed, frame = self.cam.read()
    return grabbed, frame, self.time_unit
