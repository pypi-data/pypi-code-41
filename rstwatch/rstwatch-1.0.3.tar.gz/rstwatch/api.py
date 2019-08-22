"""
rstwatch external API
"""
import itertools
import time

from .util import SourceDirectory

__all__ = ['RSTWatch']


class RSTWatch(object):
    """
    Repeatedly scan a list of directories for changes to RST
    (reStructuedText) files and generate html files from them.
    """

    def __init__(self, directories, interval=2.0, writer='html5'):
        """
        :param directories:
            List (or sequence) of directory names to watch for RST file
            changes.
        :param interval:
            Number of seconds to wait beteween directory scans.
        :param writer:
            Name of the reStructeredText writer to use, e.g. 'html' or
            'html5'.
        """
        self.directories = directories
        self.interval = interval
        self.writer = writer

    def run(self, refresh=False, one_time=False):
        """
        :param refresh:
            True to re-write all html files on the first pass, regardless of
            their modification times.
        :param one_time:
            True to exit the loop after the first pass, instead of
            continually re-scanning every ``interval`` seconds.
        """
        dir_objs = [SourceDirectory(self, directory)
                    for directory in self.directories]
        for i in itertools.count():
            for dir_obj in dir_objs:
                dir_obj.scan(refresh=((i == 0) and refresh))
            if i == 0 and one_time:
                break
            time.sleep(self.interval)
