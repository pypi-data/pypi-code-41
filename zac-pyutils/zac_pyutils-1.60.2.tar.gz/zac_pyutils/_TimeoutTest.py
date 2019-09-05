# encoding:utf-8
# author: zac
# create-time: 2019-08-27 20:59
# usage: -
import threading
from threading import Thread, Event
import time
import sys
from queue import Queue

is_py2 = sys.version[0] == '2'
if is_py2:
    print("TimeoutTest not available in py2")


############################################
# 重载Thread内部的一些方法实现真正停止子线程
# https://stackoverflow.com/questions/14482230/why-does-the-python-threading-thread-object-has-start-but-not-stop?noredirect=1&lq=1
############################################
class StopThread(StopIteration):
    pass


threading.SystemExit = SystemExit, StopThread


# 方案一
class Thread2(threading.Thread):
    def stop(self):
        self.__stop = True

    def _bootstrap(self):
        if threading._trace_hook is not None:
            raise ValueError('Cannot run thread with tracing!')
        self.__stop = False
        sys.settrace(self.__trace)
        super(Thread2, self)._bootstrap()

    def __trace(self, frame, event, arg):
        if self.__stop:
            raise StopThread()
        return self.__trace


# 方案二 | 速度更快
class Thread3(threading.Thread):
    def _bootstrap(self, stop_thread=False):
        def stop():
            nonlocal stop_thread
            stop_thread = True

        self.stop = stop

        def tracer(*_):
            if stop_thread:
                raise StopThread()
            return tracer

        sys.settrace(tracer)
        super(Thread3, self)._bootstrap()


class TimeoutThread():
    def __init__(self, target, args=(), time_limit=1, delta=0.05):
        self.resultQ = Queue()
        _target = self._put_res_in_resultQ(target)
        self.t = Thread3(target=_target, args=args)
        self.t.setDaemon(True)

        self.timing_thread = Thread3(target=self.timing, args=(time_limit,))
        self.timing_thread.setDaemon(True)

    def timing(self, timeout):
        time.sleep(timeout + 0.1)  # 多等0.1秒再kill掉进程，让达到timeout那一瞬间时的print之类的程序能执行下去
        print("timing计时完毕，kill目标子线程..")
        self.t.stop()

    def start(self):
        self.t.start()
        self.timing_thread.start()
        # 主线程block住直到self.t运行结束或者超时(self.timing_thread结束)
        while True:
            if self.t.isAlive() and self.timing_thread.isAlive():
                continue
            else:
                break
        self.t.stop()
        self.timing_thread.stop()
        q = self.resultQ.queue
        res_ = q[0] if len(q) > 0 else None
        return res_

    def _put_res_in_resultQ(self, func):
        """
        # 给target方法做个wrap，把其返回结果放到self.resultQ里
        :param func: 即target方法
        :return:
        """

        def wraps(*args, **kwargs):
            res = func(*args, **kwargs)
            print("func运行完毕，结果将要放入resultQ队列中")
            self.resultQ.put(res)

        return wraps


def func_tset_timeout(inp, timeout=5):
    for i in range(timeout):
        time.sleep(1)
        print("子线程执行中：{}".format(i))
    return inp + 100


time_limit = 3
time_during = 3
to_inp = 2
print(">>> Test TimeoutThread")
b0 = time.time()
t0 = TimeoutThread(target=func_tset_timeout, args=(to_inp, time_during), time_limit=time_limit)
result = t0.start()
print("result is {}, time:{}".format(result, time.time() - b0))
print("等待 {}秒".format(time_limit))
time.sleep(time_limit)
print("result is {}, time:{}".format(result, time.time() - b0))
print("子线程不再输出日志，的确被kill掉")

assert False


##############################################################################
# join方式 实现了一个可停止的线程，不过从子线程切回主线程，这个子线程还会继续在后台运行
##############################################################################
class StoppableThread(Thread):
    """
    会往resultQ里放两个值，先后视情况而定
    a.在target运行结束后会把结果放到resultQ里 | 这一步需要自行在target方法里写好
    b.在time_limit结束时会往resultQ里放一个None
    所以只用取resultQ的 resultQ.queue[0]，如果是None说明target运行超时
    """

    def __init__(self, resultQ, target, args=(), time_limit=1, delta=0.05):
        super(Thread, self).__init__()
        self.resultQ = resultQ
        self.delta = delta
        self.stopped = False
        self.t = Thread2(target=target, args=args)
        self.t.setDaemon(True)

        self.timing_thread = Thread2(target=self.timing, args=(time_limit,))
        self.timing_thread.setDaemon(True)

    def timing(self, timeout):
        time.sleep(timeout)
        self.stopped = True

    def start(self):
        self.t.start()
        self.timing_thread.start()
        while not self.stopped and len(self.resultQ.queue) == 0:
            self.t.join(self.delta)
            time.sleep(0.05)
        self.resultQ.put(None)
        self.t.stop()

    # def stop(self):
    #     self.stopped = True


q = Queue()


def func_tes_stoppable(inp, timeout=5):
    print("input: ", inp)
    for i in range(timeout):
        time.sleep(1)
        print(i)
    inp += 1
    print("processed: ", inp)
    q.put(inp)


time_limit = 30
time_during = 3
to_inp = 2
print(">>> Test StoppableThread")
b = time.time()
t1 = StoppableThread(resultQ=q, target=func_tes_stoppable, args=(to_inp, time_during), time_limit=time_limit)
t1.start()
print("result in queue: {}, time: {}".format(q.queue[0], time.time() - b))
time.sleep(time_during)
print("result in queue: {}, time: {}".format(q.queue[0], time.time() - b))
