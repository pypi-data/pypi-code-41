# Copyright 2018 Okera Inc.
from __future__ import absolute_import
import multiprocessing
import time
import os
import threading
import signal

def default_max_client_process_count():
  return multiprocessing.cpu_count() * 2

class ConcurrencyController(object):
  def __init__(self, worker_count=default_max_client_process_count()):
    self.pid = os.getpid()
    self.manager = multiprocessing.Manager()
    self.manager_pid = self.manager._process.pid
    self.task_queue = multiprocessing.JoinableQueue()
    self.input_queue = self.manager.Queue()
    self.output_queue = multiprocessing.Queue()
    self.errors_queue = self.manager.Queue()
    self.metrics_dict = self.manager.dict()
    self.worker_count = worker_count
    self.workers = []
    self.is_running = False

  def start(self):
    self.is_running = True
    self.workers = [ TaskHandlerProcess(parent_pid=self.pid,
                                        manager_pid=self.manager_pid,
                                        task_queue=self.task_queue,
                                        output_queue=self.output_queue,
                                        metrics_dict=self.metrics_dict,
                                        errors_queue=self.errors_queue,
                                        concurrency_ctl=self)
                    for i in range(self.worker_count) ]
    for worker in self.workers:
        worker.start()

  def stop(self):
    if self.is_running:
      self.is_running = False
      for i in range(self.worker_count):
          self.enqueueTask(task=None)
      self.task_queue.close()
      self.task_queue.join()
      self.terminate()

  def terminate(self):
    for worker in self.workers:
      worker.terminate()
      worker.join()
    self.manager.shutdown()

  def enqueueTask(self, task):
    self.task_queue.put(task)

class TaskHandlerProcess(multiprocessing.Process):

  def __init__(self,
               parent_pid,
               manager_pid,
               task_queue,
               output_queue,
               metrics_dict,
               errors_queue,
               concurrency_ctl):

    multiprocessing.Process.__init__(self)
    self.parent_pid = parent_pid
    self.manager_pid = manager_pid
    self.task_queue = task_queue
    self.output_queue = output_queue
    self.metrics_dict = metrics_dict
    self.errors_queue = errors_queue
    self.concurrency_ctl = concurrency_ctl

  def watch_dog(self):
    while self.concurrency_ctl.is_running:
      self.check_parent_process()
      time.sleep(1)

  def kill_proc(self, pid):
    try:
      os.kill(pid, signal.SIGKILL)
    except ProcessLookupError as e:
      # We expect to hit this case when a worker tries to kill a manager process
      # that would have already been killed by another worker
      pass

  def check_parent_process(self):
    if self.parent_pid != os.getppid():
      print('Parent died! Terminating Worker Process: '
            'pid={} ppid={}'.format(os.getpid(), os.getppid()))
      # First attempt to terminate the multiprocessing.Manager process which is running
      # independently from the parent and worker processes.
      self.kill_proc(self.manager_pid)
      self.kill_proc(os.getpid())

  def run(self):
    threading.Thread(target=self.watch_dog).start()

    while self.concurrency_ctl.is_running:
      next_task = self.task_queue.get()
      if next_task is None:
        # Poison pill means shutdown
        self.task_queue.task_done()
        break
      next_task.set_handler(self)
      next_task.max_records = self.metrics_dict.get('limit', None)
      answer = next_task()
      if len(next_task.errors):
        for e in next_task.errors:
          self.errors_queue.put(e)
      self.output_queue.put(answer)
      self.task_queue.task_done()

    return

class BaseBackgroundTask(object):
  def __init__(self, name):
    self._name = name
    self.handler = None

  def __call__(self):
    raise Exception('Invalid invocation of an abstract function: ' +
                    'BaseBackgroundTask::__call__')

  def __str__(self):
    return self.Name

  def set_handler(self, handler):
    self.handler = handler

  @property
  def Name(self):
    return  self._name
