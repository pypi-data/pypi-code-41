# Utility script for Google Colab

import copy        # Shallow and deep copy operations.
import datetime    # Basic date and time types.
import google
import h5py        # Read and write HDF5 files from Python.
import importlib   # The implementation of import.
import IPython     # Productive Interactive Computing.
import IPython.display
import json        # JSON encoder and decoder
import keras       # Deep Learning for humans.
import keras.backend as K
import matplotlib  # Plotting package
import matplotlib.pyplot
import matplotlib.pyplot as plt
import numpy       # The fundamental package for array computing with Python.
import numpy as np
import os          # Miscellaneous operating system interfaces.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import pandas      # Powerful data structures for data analysis, time series, and statistics.
import PIL         # Python Imaging Library. (Pillow)
import platform    # Access to underlying platform’s identifying data.
import pytz        # World timezone definitions, modern and historical.
import seaborn     # Statistical data visualization.
import shutil      # High-level file operations.
import sklearn     # A set of python modules for machine learning and data mining.
import sklearn.tree
import subprocess  # Subprocess management.
import sys         # System-specific parameters and functions.
import tensorflow  # An open source machine learning framework for everyone.
import tensorflow as tf
tensorflow.logging.set_verbosity(tensorflow.logging.ERROR)
import textwrap    # Text wrapping and filling.
import time        # Time access and conversions.

GOOGLE_DRIVE_DATA_PATH = "colab_data"
DEFAULT_TIMEZONE = pytz.timezone("Asia/Tokyo")
timezone = DEFAULT_TIMEZONE
time_greet = None

def bye():
  if time_greet:
    import datetime, time
    now = time.time()
    seconds = now - time_greet
    delta = datetime.timedelta(seconds=seconds)
    print("Bye. 前回greet()が呼ばれてから{}が経ちました。".format(get_timedelta_string(delta)))
  else:
    print("Bye.")

def get_modules():
  import sys
  return list(sorted(sys.modules))

def get_notebook_setting():
  """Returns Colab - Edit - Notebook settings; e.g. ("Python 3", "GPU")."""
  import sys
  runtime_type = "Python {}".format(sys.version_info.major)
  import os
  if "COLAB_TPU_ADDR" in os.environ:
    hardware_accelerator = "TPU"
  elif os.environ["COLAB_GPU"] == "1":
    hardware_accelerator = "GPU"
  else:
    hardware_accelerator = "None"    
  return runtime_type, hardware_accelerator

def get_python_version():
  """Returns the Python runtime version; 2 or 3."""
  import sys
  return sys.version_info.major

def get_strftime(datetime):
  """Returns e.g. "1999-12-31 Fri 23:59:59"."""
  return datetime.strftime("%Y-%m-%d %a %H:%M:%S")

def get_timedelta_string(timedelta):
  """Returns a string e.g. "12時間59分59秒"."""
  def get_h_m_s(timedelta):
    total_seconds = timedelta.total_seconds()
    h = int(total_seconds // 3600)
    m = int(total_seconds % 3600 // 60)
    s = int(total_seconds % 60 // 1)
    return h, m, s

  h, m, s = get_h_m_s(timedelta)
  
  if h > 0:
    s = "{}時間{}分{}秒".format(h, m, s)
  elif m > 0:
    s = "{}分{}秒".format(m, s)
  else:
    s = "{}秒".format(s)
  return s

def greet():
  notebook_setting = get_notebook_setting()
  print("Notebook settings:", notebook_setting)
  runtime_type, hardware_accelerator = notebook_setting
  print_versions()
  print_time_info()
  
  if hardware_accelerator == "GPU":
    run("nvidia-smi --list-gpus")
  
  remove_sample_data()
  run("ls -l /content")
  run("pwd")
  import time
  global time_greet
  time_greet = time.time()

def load(path):
  """Loads a file from Google Drive."""
  run('cp /content/drive/"My Drive"/{}/{} .'.format(GOOGLE_DRIVE_DATA_PATH, path))

def keras_callbacks():
  """Return some callbacks to pass to model.fit(callbacks=)."""
  global tensorboard_last_logdir
  import datetime, os

  def create_logdir_name():
    """Returns e.g. "logdir_991231_235959"."""
    now = datetime.datetime.now(timezone)
    s = now.strftime("logdir_%y%m%d_%H%M%S")
    return s

  logdir = os.path.join("logdir", create_logdir_name())
  board = keras.callbacks.TensorBoard(log_dir=logdir)
  return [board]

def kaggle_json(username, key):
  """Creates a file kaggle.json with the username and the key."""
  run("mkdir /root/.kaggle")
  with open("/root/.kaggle/kaggle.json", "w") as f:
    f.write('{{"username":"{}","key":"{}"}}'.format(username, key))
  run("chmod 600 /root/.kaggle/kaggle.json")

def keras_h5_summary(path="model.h5"):
  """Returns a long summary string of Keras .h5 file."""
  import h5py, json, numpy
  result = ""

  def walk(item, depth=0):
    """Walks each nodes recursively."""
    def p(s):
      """Appends a string s to the output."""
      nonlocal result
      s = str(s)
      result += depth * "  " + s + "\n"

    name = item.name  # long name like abspath.
    
    if name == "/":
      short_name = ""
    else:
      parent_name = item.parent.name
      parent_name_len = len(parent_name)

      if parent_name == "/":
        short_name = name[parent_name_len:]
      else:
        short_name = name[parent_name_len + 1:]

    if isinstance(item, h5py.Group):
      short_name += "/"
    p("{}  (i.e. {})".format(short_name, name))

    for k, v in item.attrs.items():
      if isinstance(v, bytes):
        v = v.decode("utf-8")

        if v.startswith("{"):
          json_ = json.loads(v)
          s = json.dumps(json_, indent=2)
          ss = s.split("\n")
          ss = [depth * "  " + "    " + s for s in ss]
          s = "\n".join(ss)
          p("  (attribute) {} ==".format(k))
          p(s)
        else:
          p("  (attribute) {} == {}".format(k, v))
      elif isinstance(v, numpy.ndarray):
        v = [x.decode("utf-8") for x in v]
        p("  (attribute) {} ==".format(k))

        for x in v:
          p("    {}".format(repr(x)))

    if isinstance(item, h5py.Dataset):
      value = item.value
      type_ = value.__class__.__name__
      
      if type_ == "ndarray":
        s = repr(str(value))[1:-1]  # Removes '' by [1:-1]
        
        if len(s) > 40:
          s = s[:40] + "..."
        
        p("  : {} of shape={} == {}".format(type_, value.shape, s))
      elif type_ == "int64":
        p("  : {} == {}".format(type_, value))        
      else:
        print(type_)
        raise

    if isinstance(item, h5py.Group):
      for k in item:
        child = item[k]
        walk(child, depth + 1)

  with h5py.File(path) as f:
    walk(f)
  
  return result

def keras_plot(model, prefix="model"):
  """Plots the model as a .svg."""
  import IPython.display, keras

  def summary(model, print_fn=print):
    keras.utils.print_summary(model,
                              line_length=120,
                              positions=[.25, .7, .8, 1],
                              print_fn=print_fn)

  summary(model)

  with open(prefix + "_summary.txt", "w") as f:
    summary(model,
            print_fn=lambda x: f.write(x + "\n"))

  keras.utils.plot_model(model, to_file=prefix + ".svg", show_shapes=True)
  svg = IPython.display.SVG(filename=prefix + ".svg")
  IPython.display.display(svg)

def keras_save(model):
  """Saves the model."""
  path = "model.h5"
  import os
  abspath = os.path.abspath(path)
  
  if os.path.exists(abspath):
    os.remove(abspath)
  
  assert(not os.path.exists(abspath))
  model.save(path)
  assert(os.path.exists(abspath))
  size = os.path.getsize(abspath)
  print("Saved a model: {} ({:,} bytes)".format(abspath, size))

def keras_save_mlmodel():
  """Saves the mlmodel."""
  path = "model.mlmodel"
  import os
  abspath = os.path.abspath(path)
  
  if os.path.exists(abspath):
    os.remove(abspath)
  
  assert(not os.path.exists(abspath))
  coremltools = pip_import("coremltools")
  print("convert()...")
  mlmodel = coremltools.converters.keras.convert("model.h5")
  mlmodel.save(path)
  assert(os.path.exists(abspath))
  size = os.path.getsize(abspath)
  print("Saved a mlmodel: {} ({:,} bytes)".format(abspath, size))

def magic(s):
  """Executes a Jupyter magic command s."""
  import IPython
  ipython = IPython.get_ipython()
  print_string(u"==== % {:=<93}\n".format(s + " "))
  ipython.magic(s)

def mount():
  """Enables access via /content/drive/My Drive."""
  import google
  google.colab.drive.mount('/content/drive')

def p(*args, **kwargs):
  """An alias of the standard print() function."""
  print(*args, **kwargs)

def pip_import(module_name):
  """Returns a imported module module_name. pip install if needed."""
  import importlib
  try:
    module = importlib.import_module(module_name)
  except ImportError:
    import pip._internal
    pip._internal.main(["install", module_name])
    module = importlib.import_module(module_name)
  return module

def print_environ():
  """Prints the environment key-value informations."""
  import os
  environ = os.environ  # A mapping object representing the string environment.
  max_environ = len(environ) - 1
  print("os.environ:")
  for i, (k, v) in enumerate(sorted(environ.items())):
    print("[{: >2}/{}]  {: <30} {}".format(i, max_environ, k, v))    

def print_flops():
  """Prints the model FLOPS approximation of the current model."""
  import keras
  import tensorflow
  
  graph    = keras.backend.get_session().graph
  run_meta = tensorflow.RunMetadata()
  options  = tensorflow.profiler.ProfileOptionBuilder.float_operation()
  profile  = tensorflow.profiler.profile(graph   =graph,
                                         run_meta=run_meta,
                                         cmd     ='op',
                                         options =options)
  flops = profile.total_float_ops
  print("Model FLOPS: {:,}".format(flops))

def print_string(s):
  """Prints the string s with additional newline at the end."""
  import sys
  # print(..., end="") is not exist in Python 2.
  sys.stdout.write(s)

def print_time_info():
  """uptimeについて表示する。"""
  import datetime, psutil, time
  boot_time = psutil.boot_time()
  datetime_ = datetime.datetime.fromtimestamp(boot_time, tz=timezone)
  s = "起動時刻は {} です。".format(get_strftime(datetime_))
  now = time.time()
  uptime = now - boot_time
  delta = datetime.timedelta(seconds=uptime)
  s += "起動して{}が経ちました。\n".format(get_timedelta_string(delta))
  datetime_ = datetime.datetime.fromtimestamp(now, tz=timezone)
  s += "現在時刻は {} です。".format(get_strftime(datetime_))
  remain = 12*60*60 - uptime
  delta = datetime.timedelta(seconds=remain)
  s += "残り時間は{}です。".format(get_timedelta_string(delta))
  print(s)

def print_versions():
  """Prints the versions of software components."""
  def get_os_version():
    import lsb_release
    xs = lsb_release.get_lsb_information()
    return xs["ID"], xs["RELEASE"]  # e.g. Ubuntu 18.04

  def get_python_version():
    import platform
    return "Python", platform.python_version()  # e.g. 3.6.8

  def get_cuda_version():
    import subprocess
    stdout = subprocess.check_output("nvcc --version".split()).decode("utf-8")
    return "CUDA", stdout.split()[-1][1:]  # e.g. 10.0.130

  def get_tensorflow_version():
    import tensorflow
    return "TensorFlow", tensorflow.__version__  # e.g. 1.14.0

  def get_keras_version():
    import keras
    return "Keras", keras.__version__  # e.g. 2.2.4

  xss = [get_os_version(),
         get_python_version(),
         get_cuda_version(),
         get_tensorflow_version(),
         get_keras_version()]
  import pandas
  frame = pandas.DataFrame(xss)
  print("Software versions:")
  print(frame.to_string(header=False, index=False))

def print_wrapped(s, width=100):
  """Prints a string s with its lines line-wrapped."""
  import textwrap
  lines = textwrap.wrap(s, width)
  s = "\n".join(lines)
  print(s)

def show_image(path):
  """Shows the image of the path."""
  import matplotlib.pyplot as plt
  import PIL
  image = PIL.Image.open(path)
  plt.imshow(numpy.array(image))

def remove_sample_data():
  """Removes the directory sample_data."""
  import os
  if os.path.exists("/content/sample_data"):
    run("rm -rf /content/sample_data")

def run(command, return_result=False, summary=False):
  """Runs the command. Avoids subprocess.run() for use with Python 2."""
  import subprocess, sys, time
  # Uses shell=True to avoid command.split()
  before = time.time()
  popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = popen.communicate()
  stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")

  if return_result:
    return (stdout, stderr)
    
  after = time.time()
  delta = str(int(after - before))
  print_string(u"==== $ {:=<80}={:=>8}====\n".format(command + " ", " " + delta + " s "))

  if summary:
    n_lines = len(stdout.split("\n"))
    n_chars = len(stdout)

    if n_chars < 100:
      head = repr(stdout)[1:-1]
    else:
      head = repr(stdout[:100])[1:-1] + "..."

    print_string("stdout {} lines {} characters: {}\n".format(n_lines, n_chars, head))
    print_string(stderr)
  else:
    print_string(stdout)
    print_string(stderr)

def save(path):
  """Saves a file to Google Drive."""
  run('cp {} /content/drive/"My Drive"/{}'.format(path, GOOGLE_DRIVE_DATA_PATH))

def tensorboard_plot():
  def is_tensorboard_running():
    stdout, stderr = run("ps | grep tensorboard", return_result=True)
    return "tensorboard" in stdout
    
  if not is_tensorboard_running():
    magic("load_ext tensorboard")
    import time
    time.sleep(3)
  
  magic("tensorboard --logdir=logdir")

def time_function(f, *args, **kwargs):
  """Executes the function f and times it."""
  import time
  before = time.time()
  result = f(*args, **kwargs)
  after = time.time()
  elapsed = after - before
  print("Executing {}()... {:.3g} s".format(f.__name__, elapsed))
  return result
