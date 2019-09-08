#!/usr/bin/python3
import sys
from PyQt5 import QtDBus

try:
    from .__id__ import ID, HELP
except ImportError:
    from __id__ import ID, HELP


def main():
    service = f"org.{ID}"
    path = f"/org/{ID}"
    bus = QtDBus.QDBusConnection.sessionBus()
    interface = QtDBus.QDBusInterface(service, path, "", bus)

    cmd = sys.argv[1:]
    quiet = "--no-init" in cmd or "--quiet" in cmd
    if "--help" in cmd or "-h" in cmd:
        for h in HELP:
            print(h)

    elif interface.isValid():
        interface.call("ParseCommands", cmd)
        sys.exit(0)

    elif not quiet:
        try:
            app = __import__(f"{ID}.main", fromlist=["main"])
        except ImportError:
            import main as app
        app.main(cmd)


if __name__ == '__main__':
    main()
