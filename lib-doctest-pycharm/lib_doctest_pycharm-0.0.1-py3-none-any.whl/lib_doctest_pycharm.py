import logging
import sys
logger = logging.getLogger()


def setup_doctest_logger_for_pycharm(log_level: int = logging.INFO) -> None:
    """
    >>> logger=logging.getLogger()
    >>> logger.setLevel(logging.INFO)
    >>> if is_pycharm_pytest_runner() or is_pycharm_docrunner():
    ...     setup_doctest_logger_for_pycharm()
    ...     logger.info('test')     # now we have the output we want
    ... else:
    ...     print('test')
    test

    """
    # if is_pycharm_pytest_runner() or is_pycharm_docrunner():
    # logging.getLogger().setLevel(log_level)
    # logging.getLogger('root').setLevel(log_level)
    # lib_log_utils.setup_console_logger_simple()
    # if not hasattr(logger, 'pycharm_doctest_logger_added'):
    # logger_add_streamhandler_to_sys_stdout()
    # logging.getLogger().setLevel(log_level)
    # logger.pycharm_doctest_logger_added = True

    # pycharm doctest tested OK
    # pytest.py tested OK
    if is_pycharm_docrunner() or is_pytest_py():
        logger_add_streamhandler_to_sys_stdout()
        # noinspection PyTypeHints
        logger.pycharm_doctest_logger_added = True  # type: ignore
        logging.getLogger().setLevel(log_level)
        logging.getLogger('root').setLevel(log_level)
    elif is_pycharm_pytest_runner():
        pass


def logger_add_streamhandler_to_sys_stdout() -> None:
    if not is_doctest_stdout_handler_added():
        console = logging.StreamHandler(stream=sys.stdout)
        console.name = 'doctest_console_handler'
        logging.getLogger().addHandler(console)


def is_doctest_stdout_handler_added() -> bool:
    """
    >>> setup_doctest_logger_for_pycharm()
    >>> assert is_doctest_stdout_handler_added() or not is_doctest_stdout_handler_added()

    """
    for handler in logger.handlers:
        if hasattr(handler, 'stream') and hasattr(handler, 'get_name'):
            if handler.stream == sys.stdout and handler.get_name() == 'doctest_console_handler':        # type: ignore
                return True
    return False


def is_pycharm_docrunner() -> bool:
    if 'docrunner.py' in sys.argv[0]:
        return True
    else:
        return False


def is_pycharm_pytest_runner() -> bool:
    if 'pytest_runner.py' in sys.argv[0]:
        return True
    else:
        return False


def is_pytest_py() -> bool:
    if 'pytest.py' in sys.argv[0]:
        return True
    else:
        return False
