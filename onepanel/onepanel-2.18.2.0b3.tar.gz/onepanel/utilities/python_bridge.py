import sys

py3k = sys.version_info[0] >= 3

if py3k:
    import os

    def computer_cpu_count():
        return os.cpu_count()
else:
    import multiprocessing

    def computer_cpu_count():
        return multiprocessing.cpu_count()
