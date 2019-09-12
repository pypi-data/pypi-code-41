from batchflows.CustomExceptions import ParallelFlowsException
from batchflows.threading.ExtThread import CatchThread
from batchflows.contextmanager.ContextManager import ABCContextManager, SimpleContextManager
from abc import ABC, abstractmethod
import logging
import uuid


class _Step(ABC):
    def __init__(self, name: str = None, required: bool = False):
        self.__name = name if name else str(uuid.uuid4())
        self.__required = required

    @property
    def name(self):
        return self.__name

    @abstractmethod
    def start(self, context_manager: ABCContextManager):
        pass


class Step(_Step):

    @abstractmethod
    def execute(self, _context):
        pass

    def start(self, context_manager: ABCContextManager):
        if not context_manager.is_step_done(step_name=self.name) or self.__required:
            logging.debug(f'{self.name} is running')
            self.execute(context_manager.context)
            context_manager.notify_step_done(step_name=self.name)
            logging.debug(f'{self.name} is done')
        else:
            logging.debug(f'{self.name} is already done')


class ParallelFlows(_Step):
    def __init__(self, name: str = None):
        super().__init__(name)
        self.__steps = []

    def add_step(self, step: Step):
        self.__steps.append(step)

    @property
    def steps(self):
        return self.__steps

    def __run_steps(self, context_manager: ABCContextManager):
        t_list = []
        error_list = []

        for step in self.__steps:
            trd = CatchThread(target=lambda: step.start(context_manager), name=step.name)
            trd.start()
            t_list.append(trd)

        for trd in t_list:
            trd.join()

            if trd.has_error():
                error_list.append(trd.get_error_if_exists())

        if error_list:
            raise ParallelFlowsException(self.name, error_list)

    def start(self, context_manager: ABCContextManager):
        if not context_manager.is_step_done(step_name=self.name):
            logging.debug(f'{self.name} is running')
            context_manager.notify_step_running(self.name)
            self.__run_steps(context_manager)
            context_manager.notify_step_done(self.name)
            logging.debug(f'{self.name} is done')
        else:
            logging.debug(f'{self.name} is already done')


class Batch:
    def __init__(self, name: str = None, context_manager: ABCContextManager = None, after = None):
        self.context_manager = context_manager if context_manager else SimpleContextManager()
        self.__name = name if name else str(uuid.uuid4())
        self.steps = []
        self.after = after

    @property
    def name(self):
        return self.__name

    @property
    def context(self):
        return self.context_manager.context

    def add_to_context(self, key, value):
        self.context_manager.context[key] = value

    def add_step(self, flow: _Step):
        self.steps.append(flow)

    def execute(self):
        logging.debug(f"batch_id: {self.__name} is running")
        self.context_manager.load(self.__name, self.steps)

        for step in self.steps:
            try:
                step.start(self.context_manager)
            except Exception as error:
                self.context_manager.notify_step_error(step_name=step.name)
                raise error
            finally:
                if self.after:
                    self.after()

        self.context_manager.notify_batch_done()
        logging.debug(f"batch_id: {self.__name} is done")
