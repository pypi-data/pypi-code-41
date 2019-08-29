from __future__ import absolute_import

__author__ = 'Samuel Gratzl'


def run(args):
  """
  starts celery internally
  """
  from phovea_server.config import view
  import shlex
  from .task_definition import app

  cc = view('phovea_processing_queue.celery')
  app.start([__file__] + shlex.split(cc.argv))


def create(parser):
  # no custom arguments needed
  return run
