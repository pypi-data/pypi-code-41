from tenacity import retry, wait_fixed, stop_after_attempt
import requests
from loguru import logger
import os
import time



def event_process(trigger, task, params = None, callback = None):
    params = {} if params is None else params
    trigger.bind_task(task)
    trigger.emit(**params)
    if callback:
        callback(os.getpid())

def custom_process(trigger, task, params = None, callback = None):
    params = {} if params is None else params
    trigger.bind_task(task)
    trigger.run(**params)
    if callback:
        callback(os.getpid())

def time_process(trigger, interval, task, params = None):
    params = {} if params is None else params
    trigger.bind_task(task)
    while True:
        trigger.emit(**params)
        time.sleep(interval)



class Trigger:
    DEFAULT_INTERVAL = 10

    def __init__(self, name: str, trigger_type: str, interval=None, event_name=None):
        """
        Init a trigger
        :param name: (str) Trigger's name, not repeatable
        :param trigger_type: The type of trigger, must be one of ["time","event","custom"]
        :param interval: Time interval for time trigger. Invalid for other types of triggers
        :param event_name: Event name for event trigger. Invalid for other types of triggers
        """
        # check params
        self.name = name
        if trigger_type not in ["time", "event", "custom"]:
            raise TypeError("Unsupported trigger type " + trigger_type)
        self.type = trigger_type
        if trigger_type == "time":
            if interval is None:
                print("Warning: Time trigger %s is short of interval, use default %d seconds" % (
                    name, self.DEFAULT_INTERVAL))
                self.interval = self.DEFAULT_INTERVAL
            else:
                if interval <= 0:
                    raise ValueError("Invalid interval %d, It must >=0" % interval)
                else:
                    self.interval = interval
        elif trigger_type == "event":
            if event_name is None:
                raise ValueError("Invalid event name")
            else:
                self.event = str(event_name)

        # init properties
        self.function = self.default_function
        # init from app.dump
        self.controller_url = None
        self.executor = None

    def default_function(self, *args, **kwargs):
        if not args and not kwargs:
            raise ValueError("Empty input")
        elif args:
            return args[0]
        else:
            return kwargs[kwargs.keys()[0]]



    def run(self):
        """
        Only valid when type is custom, rewrite by user, run as a process
        """
        pass


    def bind(self, func):
        """
        Bind a function for this trigger to emit
        :param func: A function or other callable object
        """
        if not hasattr(func, "__call__"):
            raise TypeError("You can only bind a callable object")
        self.function = func

    def bind_task(self, task):
        self.__task = task

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def report(self, data):
        """
        Report self status to controller
        :param data:
        :return:
        """


    def emit(self, *args, **kwargs):
        """
        Emit this trigger, and generate executor inputs
        :param args: params for bound function
        :param kwargs: params for bound function
        """
        if self.function is None:
            raise ValueError("Unbind function")
        try:
            data = self.function(*args, **kwargs)
        except:
            logger.error("Error in emit binded function: \n", exc_info=True)
            return
        try:
            self.executor.data_process(self.__task, data)
        except:
            logger.error("Error in handle data: \n", exc_info=True)
