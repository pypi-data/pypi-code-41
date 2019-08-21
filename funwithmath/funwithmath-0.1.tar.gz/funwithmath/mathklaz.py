import math
import pandas as pd

class Mathfun:

    def __init__(self,a,b):
        self.a = a
        self.b = b

    def aplusbsqrt(self):
        output = math.sqrt(self.a) + math.sqrt(self.b) + (2 * self.a * self.b)
        return output

    def aminusbsqrt(self):
        output = math.sqrt(self.a) + math.sqrt(self.b) - (2 * self.a * self.b)
        return output
