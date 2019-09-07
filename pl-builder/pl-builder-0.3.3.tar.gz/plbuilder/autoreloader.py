import os
import time
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import subprocess
import shlex
import threading


def autobuild():
    """
    Starts a process which watches for file system events on sources in the current pl-builder project, and
    automatically builds sources in response to changes.
    """
    from plbuild.paths import SOURCE_PATH
    autobuild_at_path(SOURCE_PATH)


def autobuild_at_path(watch_path: str):
    # setting up inotify and specifying path to watch
    print(f'Starting autobuilder, watching for changes in {watch_path}')
    observer = Observer()
    event_handler = AutoBuildEventHandler()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


old = 0


class AutoBuildEventHandler(FileSystemEventHandler):

    def on_modified(self, event: FileSystemEvent):
        global old
        super().on_modified(event)
        if event.src_path.endswith('.py'):
            # Watchdog has a bug where two events will be triggered very quickly for one modification.
            # Track whether it's been at least a half second since the last modification, and only then
            # consider it a valid event
            stat_buf = os.stat(event.src_path)
            new = stat_buf.st_mtime
            if (new - old) > 0.5:
                # This is a valid event, now the main logic
                self._build(event.src_path)
            old = new

    def _build(self, file_path: str):
        """
        Run build using subprocess so that imports will be executed every time
        :param file_path:
        :return:
        """
        command = f'plbuilder build {file_path}'
        run_command(command)



def run_command(command):


    p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         universal_newlines=True)

    t = threading.Thread(target=_stdout_printer, args=(p,))
    t.start()

    p.stdin.close()
    t.join()


def _stdout_printer(p):
    for line in p.stdout:
        print(line.rstrip())