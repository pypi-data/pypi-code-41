import cv2

from project.video_processors.input import VideoProcessor


class Camera(VideoProcessor):

  def __init__(self, cameraNumber):
    self.cam = cv2.VideoCapture(cameraNumber)
    self.time_unit = 0

  def get_frame(self):
    self.time_unit += 1
    grabbed, frame = self.cam.read()
    return grabbed, frame, self.time_unit


