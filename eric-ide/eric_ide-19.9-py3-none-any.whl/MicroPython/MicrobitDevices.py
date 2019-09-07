# -*- coding: utf-8 -*-

# Copyright (c) 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the device interface class for BBC micro:bit boards.
"""

from __future__ import unicode_literals

import sys
import os

from PyQt5.QtCore import pyqtSlot, QStandardPaths

from .MicroPythonDevices import MicroPythonDevice
from .MicroPythonWidget import HAS_QTCHART

from E5Gui import E5MessageBox, E5FileDialog
from E5Gui.E5Application import e5App
from E5Gui.E5ProcessDialog import E5ProcessDialog

import Utilities
import Preferences


class MicrobitDevice(MicroPythonDevice):
    """
    Class implementing the device for BBC micro:bit boards.
    """
    def __init__(self, microPythonWidget, parent=None):
        """
        Constructor
        
        @param microPythonWidget reference to the main MicroPython widget
        @type MicroPythonWidget
        @param parent reference to the parent object
        @type QObject
        """
        super(MicrobitDevice, self).__init__(microPythonWidget, parent)
    
    def setButtons(self):
        """
        Public method to enable the supported action buttons.
        """
        super(MicrobitDevice, self).setButtons()
        self.microPython.setActionButtons(
            run=True, repl=True, files=True, chart=HAS_QTCHART)
    
    def forceInterrupt(self):
        """
        Public method to determine the need for an interrupt when opening the
        serial connection.
        
        @return flag indicating an interrupt is needed
        @rtype bool
        """
        return True
    
    def deviceName(self):
        """
        Public method to get the name of the device.
        
        @return name of the device
        @rtype str
        """
        return self.tr("BBC micro:bit")
    
    def canStartRepl(self):
        """
        Public method to determine, if a REPL can be started.
        
        @return tuple containing a flag indicating it is safe to start a REPL
            and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def canStartPlotter(self):
        """
        Public method to determine, if a Plotter can be started.
        
        @return tuple containing a flag indicating it is safe to start a
            Plotter and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def canRunScript(self):
        """
        Public method to determine, if a script can be executed.
        
        @return tuple containing a flag indicating it is safe to start a
            Plotter and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def runScript(self, script):
        """
        Public method to run the given Python script.
        
        @param script script to be executed
        @type str
        """
        pythonScript = script.split("\n")
        self.sendCommands(pythonScript)
    
    def canStartFileManager(self):
        """
        Public method to determine, if a File Manager can be started.
        
        @return tuple containing a flag indicating it is safe to start a
            File Manager and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""
    
    def getWorkspace(self):
        """
        Public method to get the workspace directory.
        
        @return workspace directory used for saving files
        @rtype str
        """
        # Attempts to find the path on the filesystem that represents the
        # plugged in MICROBIT board.
        deviceDirectory = Utilities.findVolume("MICROBIT")
        
        if deviceDirectory:
            return deviceDirectory
        else:
            # return the default workspace and give the user a warning
            E5MessageBox.warning(
                self.microPython,
                self.tr("Workspace Directory"),
                self.tr("Could not find an attached BBC micro:bit.\n\n"
                        "Please make sure the device is plugged "
                        "into this computer."))
            
            return super(MicrobitDevice, self).getWorkspace()
    
    def hasTimeCommands(self):
        """
        Public method to check, if the device supports time commands.
        
        The default returns True.
        
        @return flag indicating support for time commands
        @rtype bool
        """
        return False
    
    def addDeviceMenuEntries(self, menu):
        """
        Public method to add device specific entries to the given menu.
        
        @param menu reference to the context menu
        @type QMenu
        """
        connected = self.microPython.isConnected()
        
        act = menu.addAction(self.tr("Flash Default MicroPython Firmware"),
                             self.__flashMicroPython)
        act.setEnabled(not connected)
        act = menu.addAction(self.tr("Flash Custom MicroPython Firmware"),
                             self.__flashCustomMicroPython)
        act.setEnabled(not connected)
        menu.addSeparator()
        act = menu.addAction(self.tr("Flash Script"), self.__flashScript)
        act.setToolTip(self.tr(
            "Flash the current script to the selected device."))
        act.setEnabled(not connected)
        act = menu.addAction(self.tr("Save Script as 'main.py'"),
                             self.__saveMain)
        act.setToolTip(self.tr(
            "Save the current script as 'main.py' on the connected device"))
        act.setEnabled(connected)
        menu.addSeparator()
        act = menu.addAction(self.tr("Reset micro:bit"), self.__resetDevice)
        act.setEnabled(connected)
        menu.addSeparator()
        menu.addAction(self.tr("Install 'uflash'"), self.__installUflashTool)
    
    @pyqtSlot()
    def __flashMicroPython(self):
        """
        Private slot to flash the default MicroPython firmware to the device.
        """
        flashArgs = [
            "-u",
            "-m", "uflash",
        ]
        dlg = E5ProcessDialog(self.tr("'uflash' Output"),
                              self.tr("Flash Default MicroPython Firmware"))
        res = dlg.startProcess(sys.executable, flashArgs)
        if res:
            dlg.exec_()
    
    @pyqtSlot()
    def __flashCustomMicroPython(self):
        """
        Private slot to flash a custom MicroPython firmware to the device.
        """
        downloadsPath = QStandardPaths.standardLocations(
            QStandardPaths.DownloadLocation)[0]
        firmware = E5FileDialog.getOpenFileName(
            self.microPython,
            self.tr("Flash Custom MicroPython Firmware"),
            downloadsPath,
            self.tr("MicroPython Firmware Files (*.hex);;All Files (*)"))
        if firmware and os.path.exists(firmware):
            flashArgs = [
                "-u",
                "-m", "uflash",
                "--runtime", firmware,
            ]
            dlg = E5ProcessDialog(
                self.tr("'uflash' Output"),
                self.tr("Flash Default MicroPython Firmware"))
            res = dlg.startProcess(sys.executable, flashArgs)
            if res:
                dlg.exec_()
    
    @pyqtSlot()
    def __flashScript(self):
        """
        Private slot to flash the current script onto the selected device.
        """
        aw = e5App().getObject("ViewManager").activeWindow()
        if not aw:
            return
        
        if not (aw.isPyFile() or aw.isMicroPythonFile()):
            yes = E5MessageBox.yesNo(
                self.microPython,
                self.tr("Flash Script"),
                self.tr("""The current editor does not contain a Python"""
                        """ script. Flash it anyway?"""))
            if not yes:
                return
        
        script = aw.text().strip()
        if not script:
            E5MessageBox.warning(
                self.microPython,
                self.tr("Flash Script"),
                self.tr("""The script is empty. Aborting."""))
            return
        
        if aw.checkDirty():
            filename = aw.getFileName()
            flashArgs = [
                "-u",
                "-m", "uflash",
                filename,
            ]
            dlg = E5ProcessDialog(self.tr("'uflash' Output"),
                                  self.tr("Flash Script"))
            res = dlg.startProcess(sys.executable, flashArgs)
            if res:
                dlg.exec_()
    
    @pyqtSlot()
    def __saveMain(self):
        """
        Private slot to copy the current script as 'main.py' onto the
        connected device.
        """
        aw = e5App().getObject("ViewManager").activeWindow()
        if not aw:
            return
        
        if not (aw.isPyFile() or aw.isMicroPythonFile()):
            yes = E5MessageBox.yesNo(
                self.microPython,
                self.tr("Save Script as 'main.py'"),
                self.tr("""The current editor does not contain a Python"""
                        """ script. Write it anyway?"""))
            if not yes:
                return
        
        script = aw.text().strip()
        if not script:
            E5MessageBox.warning(
                self.microPython,
                self.tr("Save Script as 'main.py'"),
                self.tr("""The script is empty. Aborting."""))
            return
        
        commands = [
            "fd = open('main.py', 'wb')",
            "f = fd.write",
        ]
        for line in script.splitlines():
            commands.append("f(" + repr(line + "\n") + ")")
        commands.append("fd.close()")
        out, err = self.microPython.commandsInterface().execute(commands)
        if err:
            E5MessageBox.critical(
                self.microPython,
                self.tr("Save Script as 'main.py'"),
                self.tr("""<p>The script could not be saved to the"""
                        """ device.</p><p>Reason: {0}</p>""")
                .format(err.decode("utf-8")))
        
        # reset the device
        self.microPython.commandsInterface().execute([
            "import microbit",
            "microbit.reset()",
        ])
    
    @pyqtSlot()
    def __resetDevice(self):
        """
        Private slot to reset the connected device.
        """
        self.microPython.commandsInterface().execute([
            "import microbit",
            "microbit.reset()",
        ])
    
    @pyqtSlot()
    def __installUflashTool(self):
        """
        Private slot to install the uflash package via pip.
        """
        pip = e5App().getObject("Pip")
        pip.installPackages(["uflash"], interpreter=sys.executable)
    
    def getDocumentationUrl(self):
        """
        Public method to get the device documentation URL.
        
        @return documentation URL of the device
        @rtype str
        """
        return Preferences.getMicroPython("MicrobitDocuUrl")
