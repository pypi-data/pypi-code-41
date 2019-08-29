# All list
__all__ = ["Clock"]

from Akuanduba.core import AkuandubaTool, StatusCode, NotSet
from Akuanduba.core.messenger.macros import *
import time

class Clock( AkuandubaTool ):

  def __init__(self, name, maxseconds):
    
    AkuandubaTool.__init__(self,name)
    self._maxseconds = maxseconds
    self._then = NotSet
    self._ntriggers = 0

  def initialize(self):

    self.getContext().setDecor("TriggerTimer", self._maxseconds)

    MSG_WARNING(self, "WARNING: This is deprecated and will be removed in the future.")

    self.init_lock()
    return StatusCode.SUCCESS


  def execute_r(self, context, accept):

    if self._then is NotSet:
      self._then = time.time()
    else:
      now = time.time()
      MSG_DEBUG(self, 'Clock: %1.2f/%1.2f seconds',(now-self._then), self._maxseconds)
      if (now-self._then) > self._maxseconds:
        self._then = NotSet
        MSG_INFO( self, "Clock triggered.")
        accept.setResult( "Clock", True )
        self._ntriggers+=1
      else:
        accept.setResult( "Clock", False )
    return StatusCode.SUCCESS


  def finalize(self):
    self.fina_lock()
    MSG_INFO( self, "Number of Clock triggers : %d", self._ntriggers )
    return StatusCode.SUCCESS