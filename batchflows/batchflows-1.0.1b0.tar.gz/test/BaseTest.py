from batchflows.Batch import Step
from batchflows.contextmanager.ContextManager import ABCContextManager
import random
import time


class ExplosiveStep(Step):
    def __init__(self):
        super().__init__()
        self.explode = False

    def execute(self, _context):
        if self.explode:
            raise Exception('Kaboom!!!')
        else:
            _context.clear()


class SaveValueStep(Step):
    def __init__(self, name: str = None, value_name: str = 'some_value', value=1, required: bool = False):
        super().__init__(name=name, required=required)
        self.value_name = value_name
        self.value = value

    def execute(self, _context):
        _context[self.value_name] = self.value


class SumCalculatorStep(Step):
    def __init__(self, name: str = None, attrs: tuple = ('value01', 'value02'), result_name: str = 'result'):
        super().__init__(name)
        self.attrs = attrs
        self.result_name = result_name

    def execute(self, _context):
        calc = 0.0
        for attr in self.attrs:
            calc += _context[attr]

        _context[self.result_name] = calc


class LazySumStep(SumCalculatorStep):
    def __init__(self, name: str = None, attrs: tuple = ('value01', 'value02'), result_name: str = 'result'):
        super().__init__(name, attrs, result_name)

    def execute(self, _context):
        time.sleep(random.randint(1, 3))
        super().execute(_context)


class TestLoadExternalContextManager(ABCContextManager):
    def load_from_external(self, batch_name: str):
        self.exec_map = {
            'unittest': True
        }

    def save_progress(self, name: str = None, status: str = None):
        pass

    def save_context(self):
        pass

    def save_batch_progress(self):
        pass


class TestSaveProgressContextManager(ABCContextManager):
    def load_from_external(self, batch_name: str):
        pass

    def save_progress(self, name: str = None, status: str = None):
        self.context['save_progress_exec'] = True

    def save_context(self):
        pass

    def save_batch_progress(self):
        pass
