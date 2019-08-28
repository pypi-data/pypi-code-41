import random

from broadcast import Broadcast


class Feature():

  def __init__(self, broadcast_name):
    self.broadcast_name = broadcast_name
    self.unique = 0

  def serialize(self):
    n = random.randint(0, 100)
    self.unique += random.randint(0, 3)
    return {"value": n, "unique": self.unique}


features = []
features.append(Feature("1"))
features.append(Feature("2"))

broadcast = Broadcast(["http://127.0.0.1:8000/api/r/camera/1/"], 3000,
                      auth="Token 8eee633d911889e6c71d966c5241e8a1a287a4bf", features=features)

broadcast.broadcast()
