import pytesseract

def text_from_img(img):
  return pytesseract.image_to_string(img)
