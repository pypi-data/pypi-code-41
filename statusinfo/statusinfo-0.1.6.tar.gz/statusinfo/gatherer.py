import logging
import re

from functools import wraps
from pathlib import Path

from .exception import StatusInfoException
from .util import run_command

logger = logging.getLogger('statusinfo')


# https://stackoverflow.com/a/30904603
def gather(icon):
    def _gather(fn):
        @wraps(fn)
        def with_icon(*args, **kwargs):
            try:
                data = fn(*args, **kwargs)
            except Exception as e:
                data = '?'
                msg = 'Exception while gathering: ' + str(e)
                logger.error(msg)

            return icon, data
        return with_icon
    return _gather


class Gatherer:
    SEPARATOR = ' '

    ICON_BACKLIGHT = ''
    ICON_GIT = ''
    ICON_MAIL = ''
    ICON_MEMORY = ''
    ICON_NEWS = ''
    ICON_SYNCHRONIZATION = ''
    ICON_TEMPERATURE = ''

    @classmethod
    @gather(ICON_BACKLIGHT)
    def gather_backlight(cls, args):
        cmd = 'brightnessctl --machine-readable get'
        stdout = run_command(cmd)
        current = int(stdout)

        cmd = 'brightnessctl --machine-readable max'
        stdout = run_command(cmd)
        maximum = int(stdout)

        percent = int((current / maximum) * 100)
        data = '{:02}%'.format(percent)

        return data

    @classmethod
    @gather(ICON_GIT)
    def gather_git(cls, args):
        if len(args) != 1:
            msg = 'Please specify exactly one source file.'
            raise StatusInfoException(msg)

        filename = args[0]

        with open(filename) as f:
            statistics = f.read()

        values = list(map(int, statistics.split(',')))

        if len(values) != 3:
            msg = 'Source file is corrupt.'
            raise StatusInfoException(msg)

        data = cls.SEPARATOR.join(map(str, values))

        return data

    @classmethod
    @gather(ICON_MAIL)
    def gather_mail(cls, args):
        counts = list()
        args.sort()

        for mailbox in args:
            cmd = 'notmuch count tag:{} and tag:unread'
            cmd = cmd.format(mailbox)
            stdout = run_command(cmd)
            count = int(stdout)
            counts.append(str(count))

        data = cls.SEPARATOR.join(counts)

        return data

    @classmethod
    @gather(ICON_MEMORY)
    def gather_memory(cls, args):
        filename = '/proc/meminfo'

        with open(filename) as f:
            meminfo = f.read()

        pattern = r'^MemTotal: \s+(\d+) kB'
        match_total = re.search(pattern, meminfo)

        pattern = r'MemAvailable: \s+(\d+) kB'
        match_free = re.search(pattern, meminfo)

        if match_total is None or match_free is None:
            raise Exception('Could not parse meminfo.')

        total = int(match_total.group(1))
        free = int(match_free.group(1))
        percent = (free / total) * 100
        percent = 100 - int(percent)
        data = '{:02}%'.format(percent)

        return data

    @classmethod
    @gather(ICON_NEWS)
    def gather_news(cls, args):
        path = '~/news/.count'
        path = Path(path)
        path = path.expanduser()

        with open(path) as f:
            data = f.read()

        data = data.strip()

        return data

    @classmethod
    @gather(ICON_SYNCHRONIZATION)
    def gather_synchronization(cls, args):
        path = '~/.local/share'
        path = Path(path)
        path = path.expanduser()

        pattern = 'sync-*.lock'
        data = path.glob(pattern)
        data = len(list(data))

        return data

    @classmethod
    @gather(ICON_TEMPERATURE)
    def gather_temperature(cls, args):
        path = '/sys/devices/platform/coretemp.0/hwmon'
        path = Path(path)
        pattern = '*/temp*_input'
        files = path.glob(pattern)
        temperatures = list()

        for f in files:
            with open(f) as f:
                temperature = f.read()

            temperature = temperature.strip()
            temperature = int(temperature)
            temperatures.append(temperature)

        data = max(temperatures) // 1000
        data = '{:02}°'.format(data)

        return data


METHOD_CHOICES = {
    'backlight': Gatherer.gather_backlight,
    'git': Gatherer.gather_git,
    'mail': Gatherer.gather_mail,
    'memory': Gatherer.gather_memory,
    'news': Gatherer.gather_news,
    'synchronization': Gatherer.gather_synchronization,
    'temperature': Gatherer.gather_temperature,
}
