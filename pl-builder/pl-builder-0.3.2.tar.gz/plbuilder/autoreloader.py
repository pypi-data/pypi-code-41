import os
import time
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from plbuilder.builder import build_by_file_path


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
                try:
                    build_by_file_path(event.src_path)
                except Exception as e:
                    print('\n')  # cancels end='' from build_by_file_path
                    print(traceback.format_exc())
                    print(f'Could not complete build for {event.src_path} due to {e.__class__.__name__}: {e}')
            old = new
