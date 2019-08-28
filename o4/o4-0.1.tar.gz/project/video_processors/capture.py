import cv2

CAMERA_ID = 0
FILENAME = 'capture'

class Camera():

  def __init__(self, cameraNumber):
    self.cam = cv2.VideoCapture(cameraNumber)
    self.time_unit = 0

  def get_frame(self):
    self.time_unit += 1
    grabbed, frame = self.cam.read()
    return grabbed, frame, self.time_unit


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


def capture(videoProcessor, save=True, name="capture"):
  if save:
    videoWriter = VideoWriter('{}.avi'.format(name))

  print("PRESS KEY 'q' TO STOP")
  while (True):
    grabbed, frame, time = videoProcessor.get_frame()

    if save:
      videoWriter.write(frame)

    cv2.imshow('Capture', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  if save:
    videoWriter.save()
  cv2.destroyAllWindows()


if __name__ == '__main__':
  videoProcessor = Camera(CAMERA_ID)
  capture(videoProcessor, save=True, name=FILENAME)
