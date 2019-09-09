from loguru import logger
import asyncio
from functools import partial
import signal
import traceback
from ..utils.async_pool import AsyncPool
import multiprocessing
import concurrent.futures

class TimeoutError(Exception):
    pass


class EnptyInputError(Exception):
    pass


class EmptyOutputError(Exception):
    pass


def default_process(inputs, config):
    return inputs


def time_limit_function(func, time_limit: int, *args, raise_error = False,  **kwargs):
    """
    Execute a function with time limit
    :param func: (callable object) The function to be executed
    :param time_limit: (int) Time limit
    :param args:  the params of the function
    :param kwargs: the params of the function
    :return:
    """

    def callback(signum, frame):
        if raise_error:
            raise TimeoutError
        else:
            return None

    signal.signal(signal.SIGALRM, callback)
    signal.alarm(time_limit)
    result = func(*args, **kwargs)
    signal.alarm(0)
    return result



def process_data(data, *args, func=default_process, timeout=1, mode="loop", pool_size=None, **kwargs):
    """
    Process data with different mode
    :param data: input data, iterable object
    :param func: process function
    :param timeout: process timeout for each input
    :param mode: process mode , one of [total, loop, async, thread, process]
    :param pool_size: pool size for mode async, thread, and process
    :param args: other params for func
    :param kwargs: other params for func
    :return:
    """
    def process_collect_result(result):
        if result is not None:
            results.append(result)

    def process_collect_error(error):
        logger.warning(error.__repr__())
        errors.append(error.__repr__())

    if mode not in ["total", "loop", "async", "thread", "process"]:
        raise ValueError("Unsupported process mod: %s, should be one of [total, loop, async, thread, process]" % mode)
    if mode in ["async", "thread", "process"] and pool_size is None:
        DEFAULT_POOL_SIZE = {"async": 100, "thread": 100, "process": 10}
        logger.warning("Unspecified pool size, use default for %s: %d", DEFAULT_POOL_SIZE[mode])
        pool_size = DEFAULT_POOL_SIZE[mode]

    results = []
    errors = []
    # switch mode
    if mode == "total":
        results = time_limit_function(func, timeout * len(data), data, *args, **kwargs)
    elif mode == "loop":
        for item in data:
            try:
                r = time_limit_function(func, timeout, item, *args, **kwargs)
                if r is not None:
                    results.append(r)
            except Exception as err:
                logger.exception(err)
                errors.append(traceback.format_exc())
    elif mode == "thread":
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=pool_size)
        tasks = [ pool.submit(func, item, *args, **kwargs) for item in data]
        for task in tasks:
            try:
                r = task.result(timeout=timeout)
                if r is not None:
                    results.append(r)
            except:
                traceback.print_exc()
                errors.append(traceback.format_exc())
    elif mode == "process":
        pool = multiprocessing.Pool(processes=pool_size)
        result = pool.map_async(partial(time_limit_function, **kwargs), [(func, timeout, item)+args for item in data],
                                callback=process_collect_result, error_callback=process_collect_error)
        result.wait()
    elif mode == "async":
        pool = AsyncPool(pool_size)
        pool.map_async(func, [(item,)+args for item in data], timeout,
                       callback=process_collect_result, error_callback=process_collect_error)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(pool.wait())

    return results, errors
