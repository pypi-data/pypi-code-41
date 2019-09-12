from abc import ABC, abstractmethod
from datetime import datetime


def sts_waiting():
    return "WAITING"


def sts_running():
    return "RUNNING"


def sts_done():
    return "DONE"


def sts_error():
    return "ERROR"


def create_step_map(steps: list):
    step_map = []
    for item in steps:
        step = {
            'name': item.name,
            'status': sts_waiting()
        }
        if hasattr(item, 'steps'):
            step['steps'] = create_step_map(item.steps)
            step['type'] = 'flow'
        else:
            step['type'] = 'single'

        step_map.append(step)

    return step_map


def get_step_by_name(steps: list, name: str):
    for step in steps:
        if step['name'] == name:
            return step
        elif step.get('steps'):
            found = get_step_by_name(step['steps'], name)
            if found:
                return found


class ABCContextManager(ABC):
    def __init__(self):
        self.context = dict()
        self.exec_map = None

    @abstractmethod
    def load_from_external(self, batch_name: str):
        raise NotImplementedError

    @abstractmethod
    def save_progress(self, step: dict):
        raise NotImplementedError

    @abstractmethod
    def save_context(self):
        raise NotImplementedError

    @abstractmethod
    def save_batch_progress(self):
        raise NotImplementedError

    def load(self, batch_name: str, steps: list):
        self.load_from_external(batch_name)
        if not self.exec_map:
            self.__create_exec_map(batch_name, steps)

    def __create_exec_map(self, batch_name: str, steps: list):
        self.exec_map = dict()
        self.exec_map['batch_name'] = batch_name
        self.exec_map['status'] = 'incomplete'
        self.exec_map['start_at'] = datetime.utcnow()
        self.exec_map['steps'] = []

        self.exec_map['steps'] = create_step_map(steps=steps)

    def is_batch_complete(self):
        return self.exec_map['status'] == 'complete'

    def is_step_done(self, step_name: str):
        step = get_step_by_name(self.exec_map['steps'], step_name)
        return step['status'] == sts_done()

    def notify_step_running(self, step_name: str):
        step = get_step_by_name(self.exec_map['steps'], step_name)
        step['status'] = sts_running()
        step['start_at'] = datetime.utcnow()
        self.save_progress(step)
        self.save_context()

    def notify_step_done(self, step_name: str):
        step = get_step_by_name(self.exec_map['steps'], step_name)
        step['status'] = sts_done()
        step['end_at'] = datetime.utcnow()
        self.save_progress(step)
        self.save_context()

    def notify_step_error(self, step_name: str):
        step = get_step_by_name(self.exec_map['steps'], step_name)
        step['status'] = sts_error()
        self.save_progress(step)
        self.save_context()

    def notify_batch_done(self):
        self.exec_map['status'] = 'complete'
        self.exec_map['end_at'] = datetime.utcnow()
        self.save_batch_progress()


class SimpleContextManager(ABCContextManager):
    def load_from_external(self, batch_name: str):
        return None

    def save_progress(self, step: dict):
        return None

    def save_context(self):
        return None

    def save_batch_progress(self):
        return None

