#!/usr/bin/python3

import sys
import cv2
from FireEye import FireEye

socket = FireEye()

cap = cv2.VideoCapture(2)

cap.set(3, 640)
cap.set(4, 480)

ret, frame = cap.read()

socket.writeImg(frame)

count = 0
while(True):
	ret, frame = cap.read()
	if count % 2:
		socket.writeImg(frame)
	count += 1
