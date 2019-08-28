import requests
from numpy.ma.bench import timer
import time
from timeit import default_timer as timer


class Broadcast():

  def __init__(self, urls, time, features=[], auth=''):
    self.urls = urls
    self.time = time / 1000
    self.features = features

    # authorization token
    self.auth = auth

    self.prev_time = timer()
    self.accum_time = 0

    self.end = False

  def broadcast(self):
    print("[Broadcast] Start")
    while True:
      if self.end:
        return

      json = {}
      for f in self.features:
        json[f.broadcast_name] = f.serialize()

      for url in self.urls:
        try:
          r = requests.post(url, json=json, headers={'Authorization': self.auth})
          print("[Broadcast] Response {}".format(r.status_code))
        except:
          print("[Broadcast] UnkownError")
          pass

      time.sleep(self.time)


  def passed_time(self):
    curr_time = timer()

    exec_time = curr_time - self.prev_time

    self.prev_time = curr_time
    self.accum_time = self.accum_time + exec_time

    if self.accum_time >= self.time:
      self.accum_time = 0
      return True

    return False

  def end(self):
    print("[Broadcast] End")
    self.end = True
