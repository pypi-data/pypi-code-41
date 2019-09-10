import logging
import datetime
from inspect import getframeinfo, stack
import os


class Log:
    logger = None
    fn_times = None

    def __init__(self):
        self.logger = logging.getLogger('psu')
        self.fn_times = {}

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        filename, line, function = self.get_caller_data()
        self.logger.error(
            "{0} -- encountered in function {1}() at {2}:{3}".format(
                msg, function, filename, line
            )
        )
        # ToDo: Also log errors in AWS database (get app name from settings)

    def trace(self, parameters=None, function_name=None):
        # If function name not specified, get it from the stack
        if function_name is None:
            function_name = self.get_calling_function()

        self.fn_times[function_name] = {'start': datetime.datetime.now()}
        params = self.get_param_string(parameters)
        self.logger.debug("TRACE : {0}({1})".format(function_name, params))
        del params

    def end(self, result=None, function_name=None):
        # If function name not specified, get it from the stack
        if function_name is None:
            function_name = self.get_calling_function()

        # If start time is known, log a completion time
        metric_txt_add_on = ""
        if function_name in self.fn_times and 'start' in self.fn_times[function_name]:
            self.fn_times[function_name]['stop'] = datetime.datetime.now()
            delta = self.fn_times[function_name]['stop'] - self.fn_times[function_name]['start']
            duration = str(int(delta.total_seconds() * 1000))
            metric_txt_add_on = f"-- completed in {duration} ms"
            del self.fn_times[function_name]

        # Only log a return value if a result was provided
        if result is not None:
            self.logger.debug(f"RETURN: {function_name}() ==> {result} {metric_txt_add_on}")

        # If no result was given, just log a completion message
        else:
            self.logger.debug(f"RETURN: {function_name}() {metric_txt_add_on}")

    def summary(self, result=None, parameters=None):
        # Get function name from the stack
        function_name = self.get_calling_function()

        # One message summarizes the function called, its parameters, and the result
        return_txt = ""
        if result is not None:
            return_txt = f" ==> {str(result)}"
        param_txt = self.get_param_string(parameters)
        self.logger.debug(f"TRACED: {function_name}({param_txt}) {return_txt}")

    def get_calling_function(self):
        filename, line, function = self.get_caller_data()
        file_basename = os.path.splitext(os.path.basename(filename))[0]
        return "{0}.{1}".format(file_basename, function)

    @staticmethod
    def get_param_string(parameters=None):

        params = str('' if parameters is None else parameters).strip()

        # Parameters are probably given in a list or dict, but may also contain a list or dict
        # Cannot strip {}[] characters because it would also strip indicators of list/dict in first/last parameter
        if params.startswith('[') and params.endswith(']'):
            params = params[1:-1]
        if params.startswith('{') and params.endswith('}'):
            params = params[1:-1]
        return params

    @staticmethod
    def get_caller_data():
        """Return the calling code as (file-name, line-number, function-name)"""

        # Ignore this function, and the Log.<function> that called it
        depth = 2

        # Get the info about the function that called the log wrapper
        caller = getframeinfo(stack()[depth][0])

        # In case of nested functions within this class, may need to look deeper
        while caller.filename.endswith('Log.py'):
            depth += 1
            caller = getframeinfo(stack()[depth][0])

        return caller.filename, caller.lineno, caller.function
