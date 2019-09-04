"""Helping to write better command-line tools
"""
__version__ = '0.0.1'

# stdlib
import logging

LOGGER = logging.getLogger(__name__)


### EXECUTOR/HANDLER HELPER FUNCTIONS ###
def log_action_finish(descript):
    LOGGER.info("Finished action: %s", descript)


def log_action(descript):
    """Used by act_if() at beginning of an action to log info message"""
    LOGGER.info("Action: %s", descript)


def log_action_skip(descript):
    """Used by act_if() to log a debug message when skipiping an action"""
    LOGGER.debug("Skipping Action: %s", descript)


def act_if(condition, func, descript=None, err_msg=None):
    """If condition is true, run function, logging the description.

    :param condition: bool (truthy value), controls whether to execute the
        value supplied to func. If truthy true, executes func, else does
        not execute it.

    :param func: callable, supply a callable value to execute.

    :optparam descript: str, supply a description of what the action is
        for. If not supplied, defaults to using the name of the function.

    :optparam err_msg: str, supply a message to add if this action
        fails, to help the user work-out what to do if it fails.

    Note:
    - If the action is executed, logs the string 'Action: <descript>'.
    - Else if the action is not executed, logs the string 'Skipping Action:
    <descript>'.
    """
    if not descript:
        # Use the function name if descript is not supplied.
        descript = func.__name__

    if condition:
        log_action(descript)
        try:
            func()
        except Exception:
            # If an err_msg is supplied, then log it. But always raise the
            # error.
            if err_msg:
                LOGGER.warn("Action %s failed. Suggestion: %s",
                            descript, err_msg)
            raise
        else:
            log_action_finish(descript)
    else:
        log_action_skip(descript)


def handler(args_namespace, exc_args, executor):
    """Calls executor function with arguments drawn from parsed namespace.

    :param exc_args: list of arguments names executor function takes. These
        executor argument-names must be exactly the same as the name on the
        args_namespace object.
        It means args_namespace names must be the same as the executors
        argument name. This makes this function a bit easier to write.

    :param executor: a callable to pass named arguments to. The executor
        function to call.

    Note:
    - Basically, takes args_namespace (which is produced when an ArgumentParser
    runs over a commandline) and converts to the argument names and values
    to keyword arguments that it then passes to the executor function.
    - The executor function takes those arguments and does whatever logic
    that command line represents. Then this function returns the return value
    of the executor.
    - The reason this is useful is the exc_args controls the names of properties
    on the args_namespace that the executor is interested in. args_namespace
    can have other properties on the object that are not a valid argument
    to the executor, e.g. global options like the --verbose flag.

    Returns returnvalue from executor.
    """
    # Use a dictionary comprehension to extract argument names and values.
    _args = {argname: getattr(args_namespace, argname) for argname in exc_args}
    logging.debug("handler calling 'executor: %s' with 'args: %s'",
                  executor.__name__, _args)
    # Unpack dictionary are keyword arguments to the executor func
    return executor(**_args)
