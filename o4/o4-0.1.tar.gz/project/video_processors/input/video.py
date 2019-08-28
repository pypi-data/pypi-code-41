from .video_processor import VideoProcessor
import cv2
import imutils


class Video(VideoProcessor):
  def __init__(self, INPUT_DIR, maxFrames=0, passFrames=1, initial_pass=0):

    self.vs = cv2.VideoCapture(INPUT_DIR)
    self.maxFrames = maxFrames
    self.nPassFrames = passFrames - 1
    self.passFrames = self.nPassFrames > 0

    # try to determine the total number of frames in the video file
    try:
      prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
        else cv2.CAP_PROP_FRAME_COUNT

      total = int(self.vs.get(prop))

      if self.maxFrames > 0:
        self.total = self.maxFrames
      else:
        self.total = (total-initial_pass) / (passFrames-1)

      print("[INFO] {} total frames in video".format(total))
    except:
      print("[INFO] could not determine # of frames in video")
      print("[INFO] no approx. completion time can be provided")
      self.total = -1

    self.nFrame = 0

    for i in range(initial_pass):
      (grabbed, frame) = self.vs.read()

  def get_frame(self):

    # pass frames
    if self.passFrames:
      for i in range(0, self.nPassFrames):
        (grabbed, frame) = self.vs.read()
    else:
      (grabbed, frame) = self.vs.read()

    self.nFrame += 1
    print("{:.1f}%".format(self.nFrame / self.total * 100))
    if not grabbed or self.nFrame == self.maxFrames:
      return False, None, self.nFrame

    return (grabbed, frame, self.nFrame)

  def close(self):
    self.vs.release()
    print("[INFO] done")
