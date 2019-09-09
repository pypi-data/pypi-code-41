import asyncio
import async_timeout
import traceback
from asyncio import Queue
from functools import reduce


async def worker(func, q, timeout=None, callback=None, error_callback=None):
    results = []
    while True:
        if q.empty():
            break
        msg = await q.get()
        result = None
        if not msg:
            await asyncio.sleep(1)
            continue
        try:
            if timeout is None:
                result = await func(*msg)
            else:
                async with async_timeout.timeout(timeout):
                    result = await func(*msg)
        except asyncio.TimeoutError as e:
            if error_callback is not None:
                error_callback(e)
            traceback.print_exc()
            q.task_done()
            continue
        except Exception as e:
            if error_callback is not None:
                error_callback(e)
            traceback.print_exc()
            q.task_done()
            continue
        if callback is not None:
            callback(result)
        if result is not None:
            results.append(result)
        q.task_done()
    return results


class AsyncPool:
    def __init__(self, pool_size):
        self.pool_size = pool_size
        self.task = None
        self.task_amount = 0

    def map_async(self, func, args, timeout=None, callback=None, error_callback=None):
        self.function = func
        self.args = args
        self.timeout = timeout
        self.callback = callback
        self.error_callback = error_callback
        self.task_amount = len(args)

    async def wait(self):
        worker_amount = min(self.pool_size, self.task_amount)
        q = Queue()
        for arg in self.args:
            if type(arg) != tuple:
                arg = (arg,)
            q.put_nowait(arg)
        tasks = []
        for _ in range(worker_amount):
            tasks.append(worker(self.function, q, timeout=self.timeout, callback=self.callback,
                                error_callback=self.error_callback))
        return reduce(lambda x, y: x + y, await asyncio.gather(*tasks))
