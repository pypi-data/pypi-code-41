import time
from contextlib import contextmanager
import signal

@contextmanager
def dont_interupt() -> None:
  old_handler = signal.getsignal(signal.SIGINT)
  signal.signal(signal.SIGINT, signal.SIG_IGN)
  try:
    yield
  finally:
    signal.signal(signal.SIGINT, old_handler)

try:
  time.sleep(10)
finally:
  #with dont_interupt():
    time.sleep(10)
    print("Hallo")
  