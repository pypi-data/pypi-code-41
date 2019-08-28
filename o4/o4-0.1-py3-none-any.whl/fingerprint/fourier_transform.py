import numpy as np
import cv2


def compare(img1, img2):
  ft1 = ft(img1)
  ft2 = ft(img2)

  sim = similarity(ft1, ft2)

  return sim


def similarity(ft1, ft2):
  ft1_shape = ft1.shape
  ft2_shape = ft2.shape

  if ft1_shape != ft2_shape:
    ft1_00 = 0
    ft1_01 = ft1_shape[0]
    ft1_10 = 0
    ft1_11 = ft1_shape[1]
    ft2_00 = 0
    ft2_01 = ft2_shape[0]
    ft2_10 = 0
    ft2_11 = ft2_shape[1]

    diff = int(abs(ft1_shape[0] - ft2_shape[0]) / 2)

    if ft1_shape[0] > ft2_shape[0]:
      ft1_00 = diff
      ft1_01 = ft2_shape[0] + diff
    else:
      ft2_00 = diff
      ft2_01 = ft1_shape[0] + diff

    diff = int(abs(ft1_shape[1] - ft2_shape[1]) / 2)

    if ft1_shape[1] > ft2_shape[1]:
      ft1_10 = diff
      ft1_11 = ft2_shape[1] + diff
    else:
      ft2_10 = diff
      ft2_11 = ft1_shape[1] + diff

    sim = 0
    for i in range(0, ft1_01 - ft1_00):
      for j in range(0, ft1_11 - ft1_10):
        sim += 1 - (abs(ft1[ft1_00 + i][ft1_10 + j] - ft2[ft2_00 + i][ft2_10 + j]))

    sim = sim / ((ft1_01 - ft1_00) * (ft1_11 - ft1_10))

  else:
    sim = np.sum(np.absolute(ft1 - ft2))

    sim = sim / (ft1.size)

  return sim


def ft(img):
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
  dft_shift = np.fft.fftshift(dft)

  magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))
  magnitude_spectrum = np.divide(magnitude_spectrum, 255)
  return magnitude_spectrum

