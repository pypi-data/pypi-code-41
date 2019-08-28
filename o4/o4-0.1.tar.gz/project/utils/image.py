import numpy as np
import cv2


def crop_img(img, left_top, right_bottom):
  cropped = img[abs(left_top[1]):abs(right_bottom[1]) + 1, abs(left_top[0]):abs(right_bottom[0]) + 1, :]
  return cropped


def crop_img_mask(img, left_top, right_bottom):
  mask = np.zeros(img.shape, np.uint8)
  mask[left_top[1]:right_bottom[1], left_top[0]:right_bottom[0]] = 255
  masked_image = cv2.bitwise_and(img, mask)

  return masked_image
