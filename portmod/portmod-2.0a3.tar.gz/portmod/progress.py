# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from threading import Thread
from queue import Queue, Empty
import time
import progressbar


# Displays a progressbar waiting for process to complete,
# update is called with the contents of each line and should return the current progress
def wait_subprocess(process, update, maxvalue):
    bar = progressbar.ProgressBar(max_value=maxvalue)
    bar.update(0)

    def enqueue_output(out, queue):
        for line in iter(out.readline, b""):
            queue.put(line)
        out.close()

    q = Queue()
    t = Thread(target=enqueue_output, args=(process.stdout, q))
    t.daemon = True  # thread dies with the program
    t.start()

    current = 0

    while process.poll() is None:
        try:
            line = q.get_nowait()  # or q.get(timeout=.1)
        except Empty:
            bar.update(current)
            time.sleep(1)
            continue

        line = line.decode("utf-8").strip()

        current = maxvalue - update(line)

        bar.update(current)

    bar.finish()
