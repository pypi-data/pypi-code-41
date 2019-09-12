from batchflows.contextmanager.LocalContextManager import FileContextManager
from batchflows.Batch import ParallelFlows, Batch
from batchflows.util.JsonUtils import DateTimeDecoder
from test.BaseTest import SaveValueStep, SumCalculatorStep, ExplosiveStep
import json
import unittest
import sys
import os
import copy

context = {
    'value01': 1,
    'value02': 2
}

flow = ParallelFlows()
flow.add_step(SaveValueStep(name='step03'))
flow.add_step(SaveValueStep(name='step04'))

steps = [
    SaveValueStep(name='step01'),
    SaveValueStep(name='step02'),
    flow
]


class FileContextManagerTest(unittest.TestCase):

    def get_separator(self):
        return '\\'

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_save_progress_win(self):
        cm = FileContextManager(os.getcwd() + '\\')
        cm.load('test_save_progress_win', steps)
        cm.context = context

        cm.save_progress()

        with open(cm.final_name, "r") as json_file:
            loaded = json.load(json_file, cls=DateTimeDecoder)

        self.assertEqual('incomplete', loaded['exec_map']['status'])
        self.assertEqual(1, loaded['context']['value01'])
        self.assertEqual('WAITING', loaded['exec_map']['steps'][0]['status'])

        cm.remove()

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_load_from_external_win(self):
        cm = FileContextManager(os.getcwd() + '\\')
        cm.load('test_load_from_external_win', steps)
        cm.context = context

        exec_map = copy.deepcopy(cm.exec_map)

        cm.save_progress()

        cm.load('test_load_from_external_win', steps)
        cm.remove()

        self.assertDictEqual(exec_map, cm.exec_map)
        self.assertDictEqual(context, cm.context)

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_load_from_external_batch_complete_win(self):
        cm = FileContextManager(os.getcwd() + '\\')
        cm.load('test_load_from_external_batch_complete_win', steps)
        cm.context = context
        cm.exec_map['status'] = 'complete'

        cm.save_progress()

        cm.load('test_load_from_external_batch_complete_win', steps)
        cm.remove()

        self.assertFalse(cm.is_batch_complete())

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_happy_batch(self):
        local_flow = ParallelFlows()
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))
        local_flow.add_step(SumCalculatorStep(attrs=('some_value', 'some_value', 'some_value')))

        local_steps = [
            SaveValueStep(),
            local_flow
        ]

        cm = FileContextManager(os.getcwd() + '\\')
        batch = Batch(context_manager=cm)
        batch.steps = local_steps

        batch.execute()

        with open(cm.final_name, "r") as json_file:
            loaded = json.load(json_file, cls=DateTimeDecoder)

        cm.remove()

        self.assertEqual('complete', loaded['exec_map']['status'])
        self.assertEqual(1, loaded['context']['some_value'])
        self.assertEqual('DONE', loaded['exec_map']['steps'][0]['status'])
        self.assertEqual('DONE', loaded['exec_map']['steps'][1]['steps'][0]['status'])

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_happy_batch(self):
        explosive = ExplosiveStep()
        local_steps = [
            SaveValueStep(),
            explosive
        ]

        cm = FileContextManager(os.getcwd() + self.get_separator())
        batch = Batch(context_manager=cm)
        batch.steps = local_steps

        explosive.explode = True
        try:
            batch.execute()
        except:
            pass

        self.assertEqual(1, cm.context['some_value'])

        explosive.explode = False

        batch.execute()

        self.assertIsNone(cm.context.get('some_value'))

        cm.remove()
