# All list
__all__ = ["TimerCondition"]

from Akuanduba.core import StatusCode, NotSet, StatusTrigger
from Akuanduba.core.messenger.macros import *
from Akuanduba.core import TriggerCondition
import time

class TimerCondition (TriggerCondition):

  def __init__(self, name, maxseconds):
    
    TriggerCondition.__init__(self, name)
    self._name = name
    self._maxseconds = maxseconds
    self._then = NotSet

  def initialize(self):

    return StatusCode.SUCCESS

  def execute (self):

    if self._then is NotSet:
      self._then = time.time()
    else:
      now = time.time()
      MSG_DEBUG(self, '%s: %1.2f/%1.2f seconds', self._name, (now-self._then), self._maxseconds)
      if (now-self._then) > self._maxseconds:
        self._then = NotSet
        MSG_DEBUG (self, "Condition {} triggered".format(self._name))
        return StatusTrigger.TRIGGERED
      else:
        return StatusTrigger.NOT_TRIGGERED

  def finalize(self):

    return StatusCode.SUCCESS