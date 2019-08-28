import math


def distance(a, b):
  return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def percentage_location(location,o4):
  return  int(location[0] * o4.WIDTH), int(location[1] * o4.HEIGHT)

def in_area(point,area):
  pass
