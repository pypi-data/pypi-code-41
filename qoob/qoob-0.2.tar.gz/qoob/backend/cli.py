#!/usr/bin/python3
from PyQt5 import QtCore, QtDBus

try:
    from ..__id__ import ID
except ValueError:
    from __id__ import ID


def parse(sysArgv):
    # Translate sys.argv arguments list to a dict of commands and arguments
    cmd, parsed = None, {}
    for arg in sysArgv:
        if arg.startswith("--"):
            cmd = arg[2:]
            parsed.setdefault(cmd, [])
        elif cmd:
            parsed[cmd].append(arg)
    return parsed


class QDBusObject(QtCore.QObject):
    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.__dbusAdaptor = QDBusServerAdapter(self, parent)
        self.start()

    def start(self):
        bus = QtDBus.QDBusConnection.sessionBus()
        bus.registerObject(f"/org/{ID}", self)
        bus.registerService(f"org.{ID}")
        return bus


class QDBusServerAdapter(QtDBus.QDBusAbstractAdaptor):
    QtCore.Q_CLASSINFO("D-Bus Interface", f"org.{ID}")
    QtCore.Q_CLASSINFO("D-Bus Introspection",
    f'<interface name="org.{ID}">\n'
    '  <method name="ParseCommands">\n'
    '    <arg direction="in" type="a{s}" name="commands"/>\n'
    '  </method>\n'
    '</interface>\n')

    def __init__(self, server, parent):
        super().__init__(server)
        self.parent = parent

    @QtCore.pyqtSlot(list)
    def ParseCommands(self, sysArgv):
        cmd = QtCore.Q_ARG(dict, parse(sysArgv))
        QtCore.QMetaObject.invokeMethod(self.parent, "cli", QtCore.Qt.QueuedConnection, cmd)
