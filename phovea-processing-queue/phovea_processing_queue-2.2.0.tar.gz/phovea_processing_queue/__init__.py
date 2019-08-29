###############################################################################
# Caleydo - Visualization for Molecular Biology - http://caleydo.org
# Copyright (c) The Caleydo Team. All rights reserved.
# Licensed under the new BSD license, available at http://caleydo.org/license
###############################################################################


def phovea(registry):
  """
  register extension points
  :param registry:
  """
  # generator-phovea:begin
  registry.append('namespace', 'phovea_processing', 'phovea_processing_queue.processing', dict(namespace='/api/processing'))
  registry.append('processing-task', 'phovea_processing_task', 'phovea_processing_queue.tasks', {})
  # register celery command
  registry.append('command', 'celery', 'phovea_processing_queue.server', {})
  # register celery security manager for my command
  registry.append('manager', 'security_manager', 'phovea_processing_queue.security', dict(command='celery', priority=1000))
  # generator-phovea:end
  pass


def phovea_config():
  """
  :return: file pointer to config file
  """
  from os import path
  here = path.abspath(path.dirname(__file__))
  config_file = path.join(here, 'config.json')
  return config_file if path.exists(config_file) else None
