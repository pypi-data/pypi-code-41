from classification.char_sequence import text_from_img
from detection.detectors.detector import Detector
import imutils
import cv2


class LicensePlateDetector(Detector):
  def detect2(self, img):
    import cv2
    # Importing the Opencv Library
    import numpy as np
    # Importing NumPy,which is the fundamental package for scientific computing with Python

    # Reading Image

    cv2.namedWindow("Original Image", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Original Image", img)
    # Display image

    # RGB to Gray scale conversion
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    cv2.namedWindow("Gray Converted Image", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Gray Converted Image", img_gray)
    # Display Image

    # Noise removal with iterative bilateral filter(removes noise while preserving edges)
    noise_removal = cv2.bilateralFilter(img_gray, 9, 75, 75)
    cv2.namedWindow("Noise Removed Image", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Noise Removed Image", noise_removal)
    # Display Image

    # Histogram equalisation for better results
    equal_histogram = cv2.equalizeHist(noise_removal)
    cv2.namedWindow("After Histogram equalisation", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("After Histogram equalisation", equal_histogram)
    # Display Image

    # Morphological opening with a rectangular structure element
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morph_image = cv2.morphologyEx(equal_histogram, cv2.MORPH_OPEN, kernel, iterations=15)
    cv2.namedWindow("Morphological opening", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Morphological opening", morph_image)
    # Display Image

    # Image subtraction(Subtracting the Morphed image from the histogram equalised Image)
    sub_morp_image = cv2.subtract(equal_histogram, morph_image)
    cv2.namedWindow("Subtraction image", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Subtraction image", sub_morp_image)
    # Display Image

    # Thresholding the image
    ret, thresh_image = cv2.threshold(sub_morp_image, 0, 255, cv2.THRESH_OTSU)
    cv2.namedWindow("Image after Thresholding", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Image after Thresholding", thresh_image)
    # Display Image

    # Applying Canny Edge detection
    canny_image = cv2.Canny(thresh_image, 250, 255)
    cv2.namedWindow("Image after applying Canny", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Image after applying Canny", canny_image)
    # Display Image
    canny_image = cv2.convertScaleAbs(canny_image)

    # dilation to strengthen the edges
    kernel = np.ones((3, 3), np.uint8)
    # Creating the kernel for dilation
    dilated_image = cv2.dilate(canny_image, kernel, iterations=1)
    cv2.namedWindow("Dilation", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Dilation", dilated_image)
    # Displaying Image

    # Finding Contours in the image based on edges
    contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    # Sort the contours based on area ,so that the number plate will be in top 10 contours
    screenCnt = None
    # loop over our contours
    for c in contours:
      # approximate the contour
      peri = cv2.arcLength(c, True)
      approx = cv2.approxPolyDP(c, 0.06 * peri, True)  # Approximating with 6% error
      # if our approximated contour has four points, then
      # we can assume that we have found our screen
      if len(approx) == 4:  # Select the contour with 4 corners
        screenCnt = approx
        break
    final = cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
    # Drawing the selected contour on the original image
    cv2.namedWindow("Image with Selected Contour", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Image with Selected Contour", final)

    # Masking the part other than the number plate
    mask = np.zeros(img_gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )
    new_image = cv2.bitwise_and(img, img, mask=mask)
    cv2.namedWindow("Final_image", cv2.WINDOW_NORMAL)
    cv2.imshow("Final_image", new_image)

    # Histogram equal for enhancing the number plate for further processing
    y, cr, cb = cv2.split(cv2.cvtColor(new_image, cv2.COLOR_RGB2YCrCb))
    # Converting the image to YCrCb model and splitting the 3 channels
    y = cv2.equalizeHist(y)
    # Applying histogram equalisation
    final_image = cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2RGB)
    # Merging the 3 channels
    cv2.namedWindow("Enhanced Number Plate", cv2.WINDOW_NORMAL)
    # Creating a Named window to display image
    cv2.imshow("Enhanced Number Plate", final_image)
    # Display image
    cv2.waitKey()  # Wait for a keystroke from the user

  def detect(self, img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grey scale
    gray = cv2.bilateralFilter(gray, 11, 30, 30)
    # cv2.imshow('gray', gray)
    edged = cv2.Canny(gray, 30, 200)  # Perform Edge detection
    cv2.imshow('edged', edged)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)

    min = 2500
    max = 70000

    screenCnt = None
    print(len(cnts))
    i = 0

    for c in cnts:
      left_top, right_bottom = self.corners(c)
      area = (right_bottom[0] - left_top[0]) * (right_bottom[1] - left_top[1])
      if area < min or area > max:
        continue
      # cv2.polylines(img, [c], True, (0, 255, 255), 4)

      # approximate the contour
      # peri = cv2.arcLength(c, True)
      # approx = cv2.approxPolyDP(c, 0.05 * peri, True)

      # left_top, right_bottom = self.corners(c)
      cv2.rectangle(img, (left_top[0], left_top[1]), (right_bottom[0], right_bottom[1]), (0, 0, 255), 9)
      # cv2.polylines(img, [approx], True, (0, 0, 255))
      cv2.imshow('img', img)
      cv2.waitKey(200)
      cropped_img = img[left_top[1]:right_bottom[1] + 1, left_top[0]:right_bottom[0] + 1]

      continue
      text = text_from_img(cropped_img)
      if text:
        print(text)
      i += 1
      # cv2.imshow('cropped' + str(i), cropped_img)

    return screenCnt

  def corners(self, array):
    left, top = right, bottom = array[0][0]

    for p in array:
      px, py = p[0]
      if px < left:
        left = px
      elif px > right:
        right = px

      if py < top:
        top = py
      elif py > bottom:
        bottom = py

    return (left, top), (right, bottom)


def test():
  import cv2
  #img = cv2.imread('../../../data/input/license_plate/amarela.jpg')
  #img = cv2.imread('../../../data/input/license_plate/nissanpolice.jpg')
  img = cv2.imread('../../../data/input/license_plate/carro.png')

  # (w,h,grayscale)=img.shape
  # img=img[int(0.59*h):int(0.63*h),int(0.25*w):int(0.39*w)]

  detector = LicensePlateDetector()
  screenCnt = detector.detect(img)
  # text_from_img(screenCnt)

  cv2.imshow('image', img)
  cv2.moveWindow('image', 40, 30)
  cv2.waitKey(0)


test()
