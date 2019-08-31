'''
Created on Jun 16, 2014

@author: lwoydziak
'''
import pexpect
import sys
from dynamic_machine.cli_commands import assertResultNotEquals, Command

        
class SshCli(object):
    LOGGED_IN = 0
    def __init__(self, host, loginUser, debug = False, trace = False, log=None, port=22, pexpectObject=None):
        self.pexpect = pexpect if not pexpectObject else pexpectObject
        self.debug = debug
        self.trace = trace
        self.host = host
        self._port = port
        self._connection = None
        self.modeList = []
        self._log = log
        self._bufferedCommands = None
        self._bufferedMode = None
        self._loginUser = loginUser
        self._resetExpect()
        
    def __del__(self):
        self.closeCliConnectionTo()
        
    def showOutputOnScreen(self):
        self.debug = True
        self.trace = True
        self._log = None
        self._setupLog()

    def connectWithSsh(self):
        self._debugLog("Establishing connection to " + self.host)
        self._connection = self.pexpect.spawn(
                'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s@%s -p %d' % 
                (self._loginUser.username, self.host, self._port))
        if self._connection is None:
            raise Exception("Unable to connect via SSH perhaps wrong IP!")
        self._secure = True
        self._setupLog()
        self._loginUser.commandLine(self)
        self.modeList = [self._loginUser]

    def resetLoggingTo(self, log):
        self._connection.logfile = log

    def _setupLog(self):
        if self.trace:
            class Python3BytesToStdOut:
                def write(self, s):
                    sys.stdout.buffer.write(s)
                def flush(self):
                    sys.stdout.flush()
            self._connection.logfile = Python3BytesToStdOut()
        if self._log is not None:
            self._connection.logfile = self._log
        
    def loginSsh(self):
        self._setupLog()
        self._debugLog("Login in as "+self._loginUser.username)

        try:
            self._loginUser.sendPassword()
            return True
        except Exception as e:
            self.forceCloseCliConnectionTo()
            raise Exception('Exception ('+str(e)+') '+'Expected CLI response: "Password:"' + "\n Got: \n" + self._lastExpect())
    
    def _exit_modes_beyond(self, thisMode):
        if not self.modeList: return
        while len(self.modeList) > thisMode + 1: 
            self.modeList.pop().exit()
    
    def exitMode(self, mode):
        if mode in self.modeList:
            self.modeList.remove(mode)
    
    def check_prereq(self, prereqMode = 0):
        self._exit_modes_beyond(prereqMode)
        if len(self.modeList) <= prereqMode:
            raise Exception("Attempted to enter menu when prerequist mode was not entered, expected: %d" % prereqMode)
        
    def execute_as(self, user):
        self.check_prereq(self.LOGGED_IN)
        self._exit_modes_beyond(self.LOGGED_IN)
        user.commandLine(self)
        user.login()
        self.modeList.append(user)
        return user
    
    def closeCliConnectionTo(self):
        if self._connection == None:
            return
        self._exit_modes_beyond(-1)
        self.modeList = []
        self._debugLog("Exited all modes.")
        self.forceCloseCliConnectionTo()
    
    def forceCloseCliConnectionTo(self):
        self.modeList = None
        if self._connection:
            self._debugLog("Closing connection.")
            self._connection.close()
        self._connection = None
        
    def _debugLog(self, message):
        if self.debug:
            print(message)

    def _resetExpect(self):
        self.previousExpectLine = ""
        if self._connection is not None and isinstance(self._connection.buffer, str):
            self.previousExpectLine = self._connection.buffer 
            self._connection.buffer = "" 
    
    def _lastExpect(self):
        constructLine = self.previousExpectLine
        if self._connection is not None and isinstance(self._connection.before, str):
            constructLine += self._connection.before
        if self._connection is not None and isinstance(self._connection.after, str):
            constructLine += self._connection.after
        return  constructLine
    
    def send(self, command):
        if self._bufferedCommands is None:
            self._bufferedCommands = command
        else:
            self._bufferedCommands += "\n" + command
        
        if self._bufferedMode is None:
            self.flush()
        else:
            self._debugLog("Buffering command " + command)
    
    def flush(self):
        if self._bufferedCommands is None:
            return
        self._connection.sendline(str(self._bufferedCommands))
        self._bufferedCommands = None
        
    def buffering(self):
        return self._bufferedMode
        
    def bufferedMode(self, mode = True):
        if mode is None:
            self.flush()
        self._bufferedMode = mode
    
    def compareReceivedAgainst(self, pattern, timeout=-1, searchwindowsize=None, indexOfSuccessfulResult=0):
        if self._bufferedMode is None:
            index = self._connection.expect(pattern, timeout, searchwindowsize)
            self._debugLog("\nLooking for " + str(pattern) + " Found ("+str(index)+")")
            self._debugLog(self._lastExpect())
            return index
        else:
            return indexOfSuccessfulResult