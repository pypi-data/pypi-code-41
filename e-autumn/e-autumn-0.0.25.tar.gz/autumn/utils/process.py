import os
import multiprocessing
from loguru import logger
from .hash import md5

def is_alive(pid):
    """
    Check For the existence of pid. 

    :param pid: a process id
    """
    try:
        os.kill(int(pid), 0)
    except:
        return False
    else:
        return True


class ErrorCollector:
    def __init__(self):
        self.errors = {}

    def add(self, key, value, times=1):
        if key not in self.errors:
            self.errors[key] = {}
        hash = md5(value)
        if hash not in self.errors[key]:
            self.errors[key][hash]={"error":value, "times": times}
        else:
            self.errors[key][hash]["times"] +=times

    def add_many(self, key, values):
        v = set(values)
        for value in v:
            self.add(key, value, times=values.count(value))

    def export(self):
        data = { key:[self.errors[key][hash] for hash in self.errors[key].keys() ] for key in self.errors.keys()}.copy()
        self.errors = {}
        return data





class Process(object):
    """
    The class Process is designed for the daemon backfround process,
    like health_check, which should be running in an independent process.

    Example:
        p = Process("health_check", action=run_health_check)
        p.start()

    :param name: the specific name of process, just for distinguishing
    :param action: the function that will run in the Process
    """

    def __init__(self, name, action=None, args=(), kwargs={}):
        action = action or (lambda x: {
            "info": "action function is not defined",
            "code": False
        })
        self.name = name
        self.action = action
        self.p = multiprocessing.Process(name=self.name,
                                         target=action, args=args,
                                         kwargs=kwargs)
        self.p.daemon = True

    @property
    def pid(self):
        """
        Get the process pid

        :returns: the pid of Process: 
        """
        return self.p.pid

    @property
    def is_running(self):
        """
        Get the process running status

        :returns: if the process is alive, the return
            value will be True, or it will be False 
        """
        return self.p.is_alive()

    def start(self):
        """
        Schedule the process to run
        """
        self.p.start()
        logger.info(
            "Process[name:{}, action:{}, pid:{}] has been started.", self.name, self.action.__name__, self.pid)

    def shutdown(self):
        """
        Schedule the process to shutdown itself
        """
        self.p.terminate()
        logger.info("Terminated the process[name:{}, action:{}, pid:{}]", self.name,
                    self.action.__name__, self.pid)
