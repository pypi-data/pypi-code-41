#!/usr/bin/python3

import sys
import cv2
import base64
from FireEye import FireEye

socket = FireEye()

cap = cv2.VideoCapture(2)

cap.set(3, 640)
cap.set(4, 480)

def encode_img(img):
	success, encoded_img = cv2.imencode('.jpg', img)
	return base64.b64encode(encoded_img)

ret, frame = cap.read()

socket.writeImg(encode_img(frame))

# count = 0
# while(True):
# 	ret, frame = cap.read()
# 	if count % 2:
# 		socket.writeImg(encode_img(frame))
# 	count += 1
