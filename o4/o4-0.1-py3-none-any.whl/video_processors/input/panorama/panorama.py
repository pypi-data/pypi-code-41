from __future__ import print_function


from project.video_processors.input import VideoProcessor


import imutils
import cv2
from . import Stitcher



class Panorama(VideoProcessor):

  def __init__(self, video1, video2):
    self.video1 = video1
    self.video2 = video2

    self.stitcher = Stitcher()
    self.total = 0

    _, imageA, _ = self.video1.get_frame()
    _, imageB, _ = self.video2.get_frame()

    imageA = imutils.resize(imageA, width=600)
    imageB = imutils.resize(imageB, width=600)

    # stitch the images together to create a panorama
    stitcher = Stitcher()
    (result, vis) = stitcher.stitch([imageA, imageB], showMatches=True)



  def get_frame(self):
    return None
    self.time_unit += 1

    grabbed, frame = self.stich()

    return grabbed, frame, self.time_unit

  def stich(self):
    _, left, _ = self.video1.get_frame()
    _, right, _ = self.video2.get_frame()

    # resize the frames
    left = imutils.resize(left, width=600)
    right = imutils.resize(right, width=600)

    # stitch the frames together to form the panorama
    # IMPORTANT: you might have to change this line of code
    # depending on how your cameras are oriented; frames
    # should be supplied in left-to-right order
    result = self.stitcher.stitch([left, right])

    # no homograpy could be computed
    if result is None:
      print("[INFO] homography could not be computed")
      return False, False

    # convert the panorama to grayscale, blur it slightly, update
    # the motion detector
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    return True, result
