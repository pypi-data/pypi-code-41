# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from .abstracts import AbstractSkippyObj
from PyTango import DevState
from threading import Thread, Event
from time import sleep
import traceback

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"

MINIMUM_RECOVERY_DELAY = 3.0


class WatchDog(AbstractSkippyObj):

    _parent = None
    _thread = None
    _work = None
    _finish = None
    _checkPeriod = None
    _recoverDelay = None

    # TODO: dynamic delay for reconnections to avoid too much retries when,
    #       for example the instrument has been shutdown. But recover asap
    #       it is back ON in a reasonable time.
    # TODO: collect information about when and why it had to act

    def __init__(self, checkPeriod=3.0,
                 recoverDelay=MINIMUM_RECOVERY_DELAY, *args, **kwargs):
        super(WatchDog, self).__init__(*args, **kwargs)
        self._checkPeriod = float(checkPeriod)
        self._recoverDelay = float(recoverDelay)
        self.__prepareEvents()
        self.__prepareThread()
        self.debug_stream("WatchDog prepared")

    @property
    def checkPeriod(self):
        return self._checkPeriod

    def __prepareEvents(self):
        self._work = Event()
        self._work.clear()
        self._finish = Event()
        self._finish.clear()

    def __prepareThread(self):
        self._thread = Thread(target=self.__doWatch, name="WatchDog")
        self._thread.setDaemon(True)

    def __doWatch(self):
        self.debug_stream("WatchDog launched")
        while not self._finish.isSet():
            if not self._work.isSet():
                self._work.wait()
            if not self.isInhibited() and not self._isInstrumentOk():
                if not self._reconnectProcedure():
                    sleep(self._checkPeriod)
            else:
                sleep(self._checkPeriod)
        self.debug_stream("Watchdog ends")

    @property
    def _communications(self):
        if self._parent is not None:
            return self._parent._communications

    def isAlive(self):
        if self._thread is not None:
            return self._thread.isAlive()
        return False

    def start(self):
        if self._thread is not None and not self.isAlive():
            self._work.set()
            self._thread.start()
            return True
        return False

    def isInhibited(self):
        # TODO: check first if the instrument has been contacted from another
        #       element of the skippylib. To avoid useless requests.
        answer = self._get_state() in [DevState.INIT, DevState.OFF]
        self.debug_stream("Watchdog is %sinhibited"
                          % ("" if answer else "not "))
        return answer

    def standby(self):
        '''This method is to avoid the connectivity check when there are
           attributes being monitored by the device. Any communication fault
           will be discovered by the monitor.
        '''
        if self._work is not None:
            self._work.clear()
            return True
        return False

    def resume(self):
        if self._work is not None and not self._work.isSet():
            self._work.set()
            return True
        return False

    def finish(self):
        if self._finish is not None:
            self._finish.set()
            return True
        return False

    def _isInstrumentOk(self):
        # TODO: check first if the instrument has been contacted from another
        #       element of the skippylib. To avoid useless requests.
        # Do it in the isInhibited()
        if self._communications is None:
            self.warn_stream("Watchdog couldn't talk with the instrument")
            return False
        if not self._communications.isConnected():
            self.warn_stream("Watchdog found the instrument disconnected")
            return False
        try:
            tries = 0
            while tries <= 1:  # two tries
                self.debug_stream("Watchdog check if instrument is there")
                idn = self._communications.ask("*IDN?")
                if idn == self._parent._idn:
                    self.debug_stream("Watchdog found the instrument ok")
                    return True
                self.warn_stream("Watchdog received a bad answer from the "
                                 "instrument (%d): %r" % (tries, idn))
                self._communications.timeBetweenSendAndReceive *= 2
                sleep(self._checkPeriod/2)  # another check in half period
                tries += 1
            self.warn_stream("Watchdog couldn't talk with the instrument (%d)"
                             % (tries))
            return False
        except Exception as e:
            self.error_stream("Watchdog had an exception checking the "
                              "instrument: %r" % (e))
            traceback.print_exc()

    def _reconnectProcedure(self):
        self.debug_stream("Launching the reconnection procedure")
        # if self._communications is not None:
        state = DevState.DISABLE
        status = "Communication with the instrument lost. "\
                 "Trying to reconnect"
        self._parent._change_state_status(newState=state, newLine=status)
        self.debug_stream("Watchdog sets a new status message: %s"
                          % (status))
        self._parent._communications = None
        if self._parent._buildCommunications(updateState=False) and \
                self._parent.connect():
            if len(self._parent.monitorObj.monitoredIds) == 0:
                self._parent._change_state_status(newState=DevState.ON)
            else:
                self._parent._change_state_status(newState=DevState.RUNNING)
            self.info_stream("Watchdog recovered the communications")
            return True
        else:
            self.warn_stream("Watchdog couldn't reconnect")
            return False
