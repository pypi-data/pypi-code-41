import queue
import threading
import time


class ScheduledTask:

    def __init__(self, task, period=None, fixed_rate=True, start=None, on_error=None, args=None, kwargs=None) -> None:
        super().__init__()
        self.task = task
        self.fixed_rate = fixed_rate
        self.period = period
        self.start = start
        self.on_error = on_error
        self.args = args or tuple()
        self.kwargs = kwargs or dict()

        self.deadline = None
        self.error = None
        self._cancelled = False

    @property
    def is_periodic(self):
        return self.period is not None

    @property
    def is_cancelled(self):
        return self._cancelled

    def set_next_deadline(self):
        if not self.deadline:
            raise ValueError('Deadline was not initialized')

        if self.fixed_rate:
            self.deadline = self.deadline + self.period
        else:
            self.deadline = time.time() + self.period

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            self.task(*self.args, **self.kwargs)
        except Exception as e:
            if self.on_error:
                self.on_error(e)


class Scheduler:
    POISON = (-1, '__POISON__')

    def __init__(self, executor=None) -> None:
        super().__init__()
        self.executor = executor

        self._queue = queue.PriorityQueue()
        self._condition = threading.Condition()

    def add(self, task: ScheduledTask):
        if task.deadline is None:
            raise ValueError

        task._cancelled = False

        with self._condition:
            self._queue.put((task.deadline, task))
            self._condition.notify()

    def schedule_task(self, task: ScheduledTask):
        task.deadline = max(task.start or 0, time.time())
        self.add(task)

    def schedule(self, func, period=None, fixed_rate=True, start=None, on_error=None, args=None,
                 kwargs=None) -> ScheduledTask:
        """
        Schedules a given task (function call).

        :param func: the task to schedule
        :param period: the period in which to run the task (in seconds). if not set, task will run once
        :param fixed_rate: whether the to run at a fixed rate (neglecting execution duration of the task)
        :param start: start time
        :param on_error: error callback
        :param args: additional positional arguments to pass to the function
        :param kwargs: additional keyword arguments to pass to the function
        :return a ScheduledTask instance
        """
        st = ScheduledTask(func, period=period, fixed_rate=fixed_rate, start=start, on_error=on_error, args=args,
                           kwargs=kwargs)
        self.schedule_task(st)
        return st

    def close(self):
        with self._condition:
            self._queue.put(self.POISON)
            self._condition.notify()

    def run(self):
        q = self._queue
        cond = self._condition
        executor = self.executor
        poison = self.POISON

        while True:
            deadline, task = q.get()

            if (deadline, task) == poison:
                break

            if task.is_cancelled:
                continue

            w = max(0, deadline - time.time())
            if w > 0:
                with cond:
                    interrupted = cond.wait(timeout=w)
                    if interrupted:
                        # something with a potentially earlier deadline has arrived
                        # the naive thing is to requeue and retry
                        # could optimize by checking the deadline of the added element(s), but that would be fairly
                        # involved. the assumption is that schedule is not invoked frequently
                        q.put((task.deadline, task))
                        continue

            if task.is_periodic:
                try:
                    task.set_next_deadline()
                except ValueError:
                    # task deadline couldn't be set because it was cancelled
                    return
                q.put((task.deadline, task))

            if not task.is_cancelled:
                if executor:
                    executor.submit(task.run)
                else:
                    task.run()
