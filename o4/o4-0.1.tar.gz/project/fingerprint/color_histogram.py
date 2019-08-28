import cv2
import numpy as np


def color_hist(img, left_top, right_bottom):
  mask = np.zeros(img.shape[:2], np.uint8)
  mask[left_top[1]:right_bottom[1], left_top[0]:right_bottom[0]] = 255

  h0 = cv2.calcHist([img], [0], mask, [10], [0, 256])
  h1 = cv2.calcHist([img], [1], mask, [10], [0, 256])
  h2 = cv2.calcHist([img], [2], mask, [10], [0, 256])

  return [h0, h1, h2]


def color_histogram(img, cells=10):
  h0 = cv2.calcHist([img], [0], None, [cells], [0, 256])
  h1 = cv2.calcHist([img], [1], None, [cells], [0, 256])
  h2 = cv2.calcHist([img], [2], None, [cells], [0, 256])

  return [h0, h1, h2]


def region_color_histogram(img, left_top, right_bottom):
  img = extract_img(img, left_top, right_bottom)
  img = img_to_regions(img)

  histograms = []
  for region in img:
    histograms.append(color_histogram(region))

  return histograms


def compare_hist(h1, h2):
  mean = 0
  for i in range(3):
    mean += cv2.compareHist(h1[i], h2[i], cv2.HISTCMP_BHATTACHARYYA)
  mean /= 3
  return mean


def compare_img(img1, img2, mask1=None, mask2=None):
  h1 = color_hist(img1, mask1)
  h2 = color_hist(img2, mask2)

  return compare_hist(h1, h2)


def compare(img1, img2, cells=10):
  h1 = color_histogram(img1, cells)
  h2 = color_histogram(img2, cells)

  return 1 - compare_hist(h1, h2)


def region_hist_compare(hists1, hists2):
  n = len(hists1)
  sim = 0
  for i in range(n):
    sim = compare_hist(hists1[i], hists2[i])

  return sim / n


def compare_region(img1, img2, cells=10):
  sim = 0
  imgs1 = img_to_regions(img1)
  imgs2 = img_to_regions(img2)

  n = len(imgs1)
  for i in range(n):
    h1 = color_histogram(imgs1[i], cells)
    h2 = color_histogram(imgs2[i], cells)

    sim += 1 - compare_hist(h1, h2)

  return sim / n


def extract_img(img, left_top, right_bottom):
  mask = np.zeros(img.shape, np.uint8)
  mask[left_top[1]:right_bottom[1], left_top[0]:right_bottom[0]] = 255
  masked_image = cv2.bitwise_and(img, mask)

  return masked_image


def img_to_regions(img, divide_lines=2, divide_columns=2):
  regions = []
  shape = img.shape

  lines = int(shape[0] / divide_lines)
  columns = int(shape[1] / divide_columns)

  for i in range(divide_lines):
    for j in range(divide_columns):
      regions.append(img[i * lines:(i + 1) * lines][j * columns:(j + 1) * columns])

  return regions
