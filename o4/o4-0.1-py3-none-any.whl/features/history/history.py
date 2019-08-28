from features.util import plotter


class History():
  def __init__(self):
    self.time_units = []
    self.history = []

  def add(self, time_unit, data):
    self.time_units.append(time_unit)
    self.history.append(data)

  def data(self, start=0, end=False, plot=False, xlabel='', ylabel=''):
    data = (self.time_units, self.history)

    if plot:
      plotter.plot(data[0], data[1], xlabel=xlabel, ylabel=ylabel)

    return data
