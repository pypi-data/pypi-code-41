# author: zac
# create-time: 2019-09-04 14:58
# usage: -
import threading
from threading import Thread, Event
import time
import sys
from queue import Queue

is_py2 = sys.version[0] == '2'
if is_py2:
    print("Timeout not available for py2")


class ThreadStopException(Exception):
    pass


class _BasicStopThread(threading.Thread):
    def _bootstrap(self, stop_thread=False):
        def stop():
            nonlocal stop_thread
            stop_thread = True

        self.stop = stop

        def tracer(*_):
            if stop_thread:
                raise ThreadStopException()
            return tracer

        sys.settrace(tracer)
        super(_BasicStopThread, self)._bootstrap()


class TimeoutThread():
    """
    使用示例：
        t2 = TimeoutThread(target=target_func, args=(30, 8), time_limit=3)
        res2=t2.start()
    """
    def __init__(self, target, args=(), time_limit=1, delta=0.05):
        self.resultQ = Queue()
        _target = self._put_res_in_result_queue(target)
        # 用来运行目标函数的线程
        self.target_thread = _BasicStopThread(target=_target, args=args)
        self.target_thread.setDaemon(True)
        # 用来计时的线程
        self.timing_thread = _BasicStopThread(target=self.timing, args=(time_limit,))
        self.timing_thread.setDaemon(True)

    def timing(self, timeout):
        time.sleep(timeout + 0.1)  # 多等0.1秒再kill掉进程，让达到timeout那一瞬间时的print之类的程序能执行下去
        # print("timing计时完毕，kill目标子线程..")
        self.target_thread.stop()

    def start(self):
        self.target_thread.start()
        self.timing_thread.start()
        # while循环block住主线程，直到self.t运行结束或者超时(self.timing_thread结束)
        while True:
            if self.target_thread.isAlive() and self.timing_thread.isAlive():
                continue
            else:
                break
        self.target_thread.stop()
        self.timing_thread.stop()
        q = self.resultQ.queue
        res_ = q[0] if len(q) > 0 else None
        return res_



    def _put_res_in_result_queue(self, func):
        """
        # 给target方法做个wrap，把其返回结果放到self.resultQ里
        :param func: 即target方法
        :return:
        """
        def wraps(*args, **kwargs):
            res = func(*args, **kwargs)
            # print("func运行完毕，结果将要放入resultQ队列中")
            self.resultQ.put(res)
        return wraps
