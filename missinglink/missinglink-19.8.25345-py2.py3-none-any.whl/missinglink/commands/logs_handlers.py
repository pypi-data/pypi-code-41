import abc
import collections

import six
from colorama import Fore, Style
from missinglink.core.api import ApiCaller, default_api_retry
from missinglink.commands.commons import output_result


@six.add_metaclass(abc.ABCMeta)
class _LogLines(object):
    LOGS_BATCH_AMOUNT = 10000

    def __init__(self, ctx):
        self._ctx = ctx
        self._last_ts = None
        self._logs_data = None

    def _load_data_if_needed(self):
        if self._logs_data is None:
            logs_data = self._api()

            if not logs_data.get('logs'):
                return False

            self._logs_data = logs_data['logs']

        return True

    def lines(self):
        while True:
            if not self._load_data_if_needed():
                break

            self._last_ts = self._logs_data[-1]['timestamp']

            for item in self._logs_data:
                yield item

            self._logs_data = None

    def _api(self):
        from six.moves.urllib.parse import urlencode

        read_logs_path = self._api_url()

        params = collections.OrderedDict()
        params['amount'] = self.LOGS_BATCH_AMOUNT

        if self._last_ts is not None:
            params['timestamp'] = self._last_ts

        read_logs_path += '?' + urlencode(params)

        return ApiCaller.call(self._ctx.obj, self._ctx.obj.session, 'get', read_logs_path, retry=default_api_retry())

    @abc.abstractmethod
    def _api_url(self):
        """"
        """


class ExperimentLogLines(_LogLines):
    def __init__(self, ctx, project, experiment):
        super(ExperimentLogLines, self).__init__(ctx)
        self._project = project
        self._experiment = experiment

    def _api_url(self):
        return 'projects/{project_id}/experiments/{experiment_id}/logs/read'.format(
            project_id=self._project, experiment_id=self._experiment)


class JobLogLines(_LogLines):
    def __init__(self, ctx, job_id):
        super(JobLogLines, self).__init__(ctx)
        self._job_id = job_id

    def _api_url(self):
        return 'run/{job_id}/logs/read'.format(job_id=self._job_id)


class LogFormatter(object):
    def __init__(self, disable_colors):
        self._disable_colors = disable_colors

    @classmethod
    def _get_color(cls, level, disable_colors):
        if disable_colors:
            return ''

        color = Style.RESET_ALL + Fore.WHITE

        levels = {
            'ERROR': Style.RESET_ALL + Fore.RED,
            'INFO': Style.RESET_ALL + Style.DIM,
            'WARNING': Style.RESET_ALL + Fore.YELLOW
        }

        return levels.get(level, color)

    @classmethod
    def __get_message(cls, category, level):
        if category is not None and level is not None:
            msg = '{ts} [{category} {level}] {message}'
        else:
            msg = '{ts} {message}'

        return msg

    def format(self, category, level, timestamp, message, disable_colors=None):
        msg = self.__get_message(category, level)

        if disable_colors is None:
            disable_colors = self._disable_colors

        color = self._get_color(level, disable_colors)

        return color + msg.format(ts=timestamp, category=category, level=level, message=message)


class LogFormatterFragments(LogFormatter):
    DEFAULT_COLOR = '#e5e5e5'

    LOG_LEVEL_COLORS = {
        'ERROR': '#7f0000',
        'INFO': '#ffffff',
        'WARNING': '#ffff00'
    }

    @classmethod
    def _get_color(cls, level, disable_colors):
        if disable_colors:
            return ''

        return cls.LOG_LEVEL_COLORS.get(level, cls.DEFAULT_COLOR)

    def fragments(self, category, level, timestamp, message):
        msg = self.format(category, level, timestamp, message, disable_colors=True)

        color = self._get_color(level, self._disable_colors)

        return [(color, msg + '\n')]


def _run_pager(line_gen):
    from missinglink.commands.utilities.whaaaaat.pypager.pager import Pager
    from missinglink.commands.utilities.whaaaaat.pypager.source import GeneratorSource

    p = Pager()
    p.add_source(GeneratorSource(line_gen))
    p.run()


def _pages_logs(ctx, lines, disable_colors):
    if ctx.obj.output_format is not None:
        return False

    customer_formatter = LogFormatterFragments(disable_colors)

    def lines_wrapper():
        for item in lines:
            yield customer_formatter.fragments(**item)

    _run_pager(lines_wrapper())

    return True


def _use_logs_api(ctx, lines_klass, disable_colors):
    lines = lines_klass.lines()

    if _pages_logs(ctx, lines, disable_colors):
        return True

    output_result(ctx, lines)

    return True


def experiment_use_logs_api(ctx, project, experiment, disable_colors):
    get_experiments_path = 'projects/{project_id}/experiments/{experiment_id}'.format(project_id=project, experiment_id=experiment)
    experiment_data = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', get_experiments_path, retry=default_api_retry())

    if not experiment_data['status'] in ['done', 'stopped', 'failed']:
        return False

    return _use_logs_api(ctx, ExperimentLogLines(ctx, project, experiment), disable_colors)


def job_use_logs_api(ctx, org, job, disable_colors):
    get_job_path = '{org}/job/{job}'.format(org=org, job=job)
    job_data = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', get_job_path, retry=default_api_retry())

    if not job_data['data']['state'] in ['done', 'removed', 'failed']:
        return False

    return _use_logs_api(ctx, JobLogLines(ctx, job), disable_colors)
