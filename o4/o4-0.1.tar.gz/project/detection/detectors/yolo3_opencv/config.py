import os
import numpy as np
import cv2


def load_model():
  # load the COCO class labels our YOLO model was trained on
  labelsPath = os.getcwd() + "\detection\detectors\yolo3_opencv\yolo-coco\coco.names"
  LABELS = open(labelsPath).read().strip().split("\n")


  # derive the paths to the YOLO weights and model configuration
  weightsPath = os.getcwd() + "\detection\detectors\yolo3_opencv\yolo-coco\yolov3.weights"
  configPath = os.getcwd() + "\detection\detectors\yolo3_opencv\yolo-coco\yolov3.cfg"

  # load our YOLO object detector trained on COCO dataset (80 classes)
  # and determine only the *output* layer names that we need from YOLO
  print("[INFO] loading YOLO from disk...")
  net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
  ln = net.getLayerNames()
  ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]


  return net, ln, LABELS
