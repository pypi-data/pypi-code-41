import matplotlib.pyplot as plt


# https://matplotlib.org/tutorials/introductory/pyplot.html

def plot(time_units, data, xlabel='', ylabel=''):
  plt.plot(time_units, data)

  plt.xlabel(xlabel)
  plt.ylabel(ylabel)
  plt.show()
  pass
