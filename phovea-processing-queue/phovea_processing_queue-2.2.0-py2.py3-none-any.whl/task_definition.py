from __future__ import absolute_import, print_function
import functools
import redis
from celery.result import AsyncResult
from celery import Task
from celery.utils.log import get_task_logger

_log = get_task_logger(__name__)


def _create_celery():
  from celery import Celery
  from phovea_server.plugin import list as list_plugins
  from phovea_server.config import view as config_view

  # set configured registry
  plugins = list_plugins('processing-task')
  cc = config_view('phovea_processing_queue')
  print(cc.get('celery.name'),
        cc.get('celery.broker'),
        cc.get('celery.backend'))

  def _map(p):
    # print 'add processing tasks: ' + p.module
    _log.info('add processing task: %s', p.module)
    return p.module

  task_modules = map(_map, plugins)

  app = Celery(cc.get('celery.name'),
               broker=cc.get('celery.broker'),
               backend=cc.get('celery.backend'),
               include=task_modules
               )

  # Optional configuration, see the application user guide.
  app.conf.update(CELERY_TASK_RESULT_EXPIRES=cc.getint('celery.expires'))
  return app


class TaskNotifier(object):
  """
  utility to encapsulate the notifier behavior using redis pub usb
  """

  def __init__(self):
    from phovea_server.plugin import lookup
    from phovea_server.config import view as config_view
    # call lookup to enforce registry initialization which triggers configuration initialization
    lookup('test')
    cc = config_view('phovea_processing_queue.celery')
    self._db = redis.Redis(host=cc.host, port=cc.port, db=cc.db)
    self._channel_name = 'phovea_processing_channel'

  def listen(self):
    """
    listens to tasks changes
    :return: a generator for notifications
    """
    import json
    p = self._db.pubsub(ignore_subscribe_messages=True)
    p.subscribe(self._channel_name)
    for msg in p.listen():
      if msg['type'] == 'message':
        yield json.loads(msg['data'])

  def send(self, task_id, task_name, task_status):
    """
    send a task change
    :param task_id:  task id
    :param task_name:  task name
    :param task_status: the status (success, failure)
    :return:
    """
    # send a message using redis
    # print('send', task_id, task_name, task_status)
    msg = '{{ "task_id": "{}", "task_name": "{}", "task_status": "{}" }}'.format(task_id, task_name, task_status)
    self._db.publish(self._channel_name, msg)


def _create_context():
  from phovea_server.security import current_user
  context = dict()

  # copy the user into the context if the user is logged in
  user = current_user()
  if user.is_authenticated:
    context['user'] = user.id
    context['roles'] = user.roles

  return context


def _take_down_context(context):
  from .security import logout_task
  if 'user' in context:
    logout_task()


def _setup_context(context):
  from .security import login_task
  if 'user' in context:
    current_log = get_task_logger(__name__)
    current_log.info('authenticating task as %s', context['user'])
    login_task(context['user'], context.get('roles', []))


class BaseTask(Task):
  """
  base class for processing tasks that report automatically when they are done using redis
  """
  abstract = True

  def on_success(self, retval, task_id, args, kwargs):
    notifier.send(task_id, self.name, 'success')

  def on_failure(self, exc, task_id, args, kwargs, einfo):
    notifier.send(task_id, self.name, 'failure')

  def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                  link=None, link_error=None, **options):
    """ invoked either directly or via .delay() to fork a task from the main process """

    # based on https://chase-seibert.github.io/blog/2015/07/24/custom-celery-arguments.html
    options['headers'] = options.get('headers', {})
    options['headers']['_phovea_processing_context'] = _create_context()

    return super(BaseTask, self).apply_async(args, kwargs, task_id, producer, link, link_error, **options)

  def __call__(self, *args, **kwargs):
    """ execute the task body on the remote worker """
    context = (self.request or {}).get('_phovea_processing_context', {})
    try:
      _setup_context(context)
      return super(BaseTask, self).__call__(*args, **kwargs)
    finally:
      _take_down_context(context)


# create a notifier instance
notifier = TaskNotifier()

# create celery
app = _create_celery()

# use my base class all the time
task = functools.partial(app.task, base=BaseTask)

# use common name
getLogger = get_task_logger


def get_result(task_id):
  """
  wrapper around AsyncResult to avoid importing
  :param task_id:
  :return:
  """
  return AsyncResult(task_id, app=app)


# just expose the needed stuff
__all__ = ['task', 'app', 'BaseTask', 'notifier', 'getLogger', 'get_result']
