import cv2


class VideoWriter():
  def __init__(self, OUTPUT_DIR):
    self.OUTPUT_DIR = OUTPUT_DIR
    self.setup_done = False

  def setup(self, frame_shape):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    self.writer = cv2.VideoWriter(self.OUTPUT_DIR, fourcc, 30,
                                  (frame_shape[1], frame_shape[0]), True)

  def write(self, frame):
    if not self.setup_done:
      self.setup(frame.shape)
      self.setup_done = True

    self.writer.write(frame)

  def save(self):
    print("[INFO] saving video ...")
    self.writer.release()
