"""restartsh - """

__version__ = '0.1.0'
__author__ = 'fx-kirin <fx.kirin@gmail.com>'
__all__ = []

import logging
import threading
import time

import delegator

logger = logging.getLogger('restartsh')


def restart_thread(cmd, flag, interval=0):
    while not flag.is_set():
        logger.info('Start [CMD]:%s', cmd)
        result = delegator.run(cmd)
        logger.info('Finished [CMD]:%s', cmd)
        if result.ok:
            logger.info('[OUT]%s', result.out)
        else:
            logger.error('[ERR]%s', result.err)
        if (interval > 0):
            logger.info('Sleep %d sec [CMD]', interval)
            time.sleep(interval)
    logger.info("Close by exit_flag")


def restarter(cmd, interval=0):
    flag = threading.Event()
    thread = threading.Thread(target=restart_thread, args=(cmd, flag, interval))
    thread.daemon = True
    thread.start()
    thread.exit_flag = flag

    return thread
