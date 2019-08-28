import cv2


def show_frame(frame,name='O4'):

  cv2.namedWindow(name, cv2.WINDOW_AUTOSIZE)
  frame = cv2.resize(frame, (960, 540))
  cv2.imshow(name, frame)

  if cv2.waitKey(1) & 0xFF == ord('q'):
    cv2.destroyAllWindows()


def close():
  cv2.destroyAllWindows()
