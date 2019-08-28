from collections import defaultdict

import os
import cv2

from project.utils import crop_img


class Dataset():

  def __init__(self, dir, occurences=None, start_index=1, object_types=[]):
    self.dir = dir
    self.occurences = occurences
    self.start_index = start_index
    self.objects = defaultdict(list)
    self.object_types = object_types

  def add(self, frame, detections):
    for d in detections:
      if self.object_types and d.className not in self.object_types:
        continue

      id = d.id
      croppedImg = crop_img(frame,d.left_top,d.right_bottom)
      self.objects[id].append(croppedImg)

  def save(self):
    print("[INFO] saving dataset on {}".format(os.path.abspath(self.dir)))

    self.create_dir(self.dir)
    i = self.start_index

    for id in self.objects:

      imgs = self.objects[id]

      if self.occurences != None and len(imgs) < self.occurences:
        continue

      dirname = '{}/{}/'.format(self.dir, i)
      self.create_dir(dirname)

      if self.occurences is None:
        passImg = 1
      else:
        passImg = len(imgs) / (self.occurences)

      j = 0
      k = 0
      while j < len(imgs):
        cv2.imwrite('{}{}.png'.format(dirname, k), imgs[int(j)])
        k += 1
        j += passImg

      i += 1

  def create_dir(self, dirname):
    try:
      os.mkdir(dirname)
    except:
      pass
