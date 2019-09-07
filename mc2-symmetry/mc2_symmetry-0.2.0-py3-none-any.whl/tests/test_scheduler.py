import threading
import time
import unittest
from concurrent.futures.thread import ThreadPoolExecutor

from symmetry.common.scheduler import Scheduler, ScheduledTask


def poll(condition, timeout=None, interval=0.5):
    remaining = 0
    if timeout is not None:
        remaining = timeout

    while not condition():
        if timeout is not None:
            remaining -= interval

            if remaining <= 0:
                raise TimeoutError('gave up waiting after %s seconds' % timeout)

        time.sleep(interval)


class DummyTask:
    def __init__(self, fn=None) -> None:
        super().__init__()
        self.i = 0
        self.invocations = list()
        self.completions = list()
        self.fn = fn

    def __call__(self, *args, **kwargs):
        self.invoke(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        self.i += 1
        invoked = time.time()
        self.invocations.append((self.i, invoked, args, kwargs))

        if self.fn:
            self.fn(*args, **kwargs)

        self.completions.append((self.i, time.time(), args, kwargs))


class TestScheduler(unittest.TestCase):
    dispatcher: ThreadPoolExecutor

    def setUp(self) -> None:
        self.dispatcher = ThreadPoolExecutor(4)

    def tearDown(self) -> None:
        self.dispatcher.shutdown()

    def create_and_start(self):
        scheduler = Scheduler(executor=self.dispatcher)
        thread = threading.Thread(target=scheduler.run)
        thread.start()

        return scheduler, thread

    def test_single_scheduled_run(self):
        scheduler, thread = self.create_and_start()

        task = DummyTask()
        invocation_time = time.time() + 0.2

        scheduler.schedule(task, start=invocation_time)

        poll(lambda: len(task.invocations) >= 1, timeout=5)

        scheduler.close()
        thread.join(5)

        self.assertEqual(1, len(task.invocations))
        self.assertEqual(1, task.invocations[0][0])
        self.assertAlmostEqual(invocation_time, task.invocations[0][1], delta=0.1)

    def test_period_run_nonfixed(self):
        task = DummyTask()
        scheduler, thread = self.create_and_start()

        scheduler.schedule(task, period=0.1, fixed_rate=False)
        scheduler.schedule(scheduler.close, start=time.time() + 0.5)
        thread.join(5)

        self.assertAlmostEqual(task.invocations[1][1] + 0.1, task.invocations[2][1], delta=0.05)
        self.assertAlmostEqual(task.invocations[2][1] + 0.1, task.invocations[3][1], delta=0.05)
        self.assertAlmostEqual(task.invocations[3][1] + 0.1, task.invocations[4][1], delta=0.05)

    def test_periodic_run_fixed_with_longer_task(self):
        task = DummyTask(fn=lambda: time.sleep(1))

        scheduler, thread = self.create_and_start()

        scheduler.schedule(task, period=0.5, fixed_rate=True)
        scheduler.schedule(scheduler.close, start=time.time() + 1.25)

        thread.join(5)

        self.assertEqual(3, len(task.invocations))

        first = task.invocations[0][1]
        self.assertAlmostEqual(first + 0.5, task.invocations[1][1], delta=0.1)
        self.assertAlmostEqual(first + 1, task.invocations[2][1], delta=0.1)

        poll(lambda: len(task.completions) >= 3, timeout=5)

    def test_periodic_change_period(self):
        task = DummyTask()
        scheduler, thread = self.create_and_start()

        stask = scheduler.schedule(task, period=1, fixed_rate=True)

        def change_period(t: ScheduledTask, period: float):
            t.period = period

        scheduler.schedule(change_period, start=time.time() + 1.25, args=(stask, 0.5))
        scheduler.schedule(scheduler.close, start=time.time() + 3)

        thread.join(5)

        first = task.invocations[0][1]
        second = task.invocations[1][1]
        third = task.invocations[2][1]
        fourth = task.invocations[3][1]
        self.assertAlmostEqual(first + 1, second, delta=0.1)
        self.assertAlmostEqual(second + 1, third, delta=0.1)
        # changed to 0.5
        self.assertAlmostEqual(third + 0.5, fourth, delta=0.1)

    def test_cancel_task(self):
        task1 = DummyTask()
        task2 = DummyTask()
        scheduler, thread = self.create_and_start()

        scheduler.schedule(task2.invoke, period=0.5)
        stask = scheduler.schedule(task1.invoke, period=0.5)

        scheduler.schedule(stask.cancel, start=time.time() + 0.75)
        scheduler.schedule(scheduler.close, start=time.time() + 1.5)

        thread.join(5)

        self.assertEqual(2, len(task1.invocations))
        self.assertEqual(4, len(task2.invocations))

    def test_error_handler(self):
        scheduler = Scheduler()

        event = threading.Event()

        def invoke():
            raise ValueError('unittest')

        def on_error(e):
            event.set()

        scheduler.schedule(invoke, on_error=on_error)
        scheduler.schedule(scheduler.close)

        scheduler.run()

        self.assertTrue(event.wait(5))

    def test_scheduling_reordering(self):
        task = DummyTask()
        scheduler, thread = self.create_and_start()

        t = time.time()
        scheduler.schedule(task, args=('task2',), start=t + 1)  # task two gets scheduled first
        time.sleep(0.25)
        scheduler.schedule(task, args=('task1',), start=t + 0.5)  # but task one has the shorter deadline

        scheduler.schedule(scheduler.close, start=t + 1.5)

        thread.join(5)

        self.assertEqual(2, len(task.invocations))
        self.assertEqual('task1', task.invocations[0][2][0])
        self.assertEqual('task2', task.invocations[1][2][0])

    def test_close_interrupts_waiting_tasks(self):
        task = DummyTask()
        scheduler, thread = self.create_and_start()

        scheduler.schedule(task, start=time.time() + 1)
        time.sleep(0.25)
        scheduler.close()

        thread.join(5)

        self.assertEqual(0, len(task.invocations))


if __name__ == '__main__':
    unittest.main()
