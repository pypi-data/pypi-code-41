import logging
import unittest

from batchflows.Batch import Batch, ParallelFlows
from batchflows.contextmanager.ContextManager import SimpleContextManager, create_step_map, get_step_by_name
from test.BaseTest import SaveValueStep, TestLoadExternalContextManager

flow = ParallelFlows(name='flow01')
flow.add_step(SaveValueStep(name='step03'))

steps = [
    SaveValueStep(name='step01'),
    flow
]


class ContextManagerTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.ERROR)

    def test_happy_path(self):
        context = SimpleContextManager()

        batch = Batch(context_manager=context)
        batch.steps = steps
        batch.execute()

        self.assertEqual('complete', context.exec_map['status'])
        self.assertIsNotNone(context.exec_map['start_at'])
        self.assertIsNotNone(context.exec_map['end_at'])

        self.assertEqual('step01', context.exec_map['steps'][0]['name'])
        self.assertEqual('DONE', context.exec_map['steps'][0]['status'])

        self.assertEqual('flow01', context.exec_map['steps'][1]['name'])
        self.assertEqual('DONE', context.exec_map['steps'][1]['status'])

        self.assertEqual('step03', context.exec_map['steps'][1]['steps'][0]['name'])
        self.assertEqual('DONE', context.exec_map['steps'][1]['steps'][0]['status'])

    def test_create_steps_map(self):
        step_map = create_step_map(steps)

        self.assertEqual('step01', step_map[0]['name'])
        self.assertEqual('WAITING', step_map[0]['status'])

        self.assertEqual('flow01', step_map[1]['name'])
        self.assertEqual('WAITING', step_map[1]['status'])

        self.assertEqual('step03', step_map[1]['steps'][0]['name'])
        self.assertEqual('WAITING', step_map[1]['steps'][0]['status'])

    def test_get_step_by_name(self):
        step_map = create_step_map(steps)
        step01 = get_step_by_name(step_map, 'step01')
        flow01 = get_step_by_name(step_map, 'flow01')
        step03 = get_step_by_name(step_map, 'step03')

        self.assertEqual('step01', step01['name'])
        self.assertEqual('flow01', flow01['name'])
        self.assertEqual('step03', step03['name'])

    def test_load_from_external(self):
        context = TestLoadExternalContextManager()
        context.load('noname', steps)

        self.assertTrue(context.exec_map['unittest'])

    def test__create_exec_map(self):
        context = SimpleContextManager()
        context.load('unittest', steps)

        self.assertEqual('unittest', context.exec_map['batch_name'])
        self.assertEqual('incomplete', context.exec_map['status'])
        self.assertIsNotNone(context.exec_map['start_at'])

        self.assertEqual('step01', context.exec_map['steps'][0]['name'])
        self.assertEqual('WAITING', context.exec_map['steps'][0]['status'])

        self.assertEqual('flow01', context.exec_map['steps'][1]['name'])
        self.assertEqual('WAITING', context.exec_map['steps'][1]['status'])

        self.assertEqual('step03', context.exec_map['steps'][1]['steps'][0]['name'])
        self.assertEqual('WAITING', context.exec_map['steps'][1]['steps'][0]['status'])

    def test_is_step_done(self):
        context = SimpleContextManager()
        context.load('unittest', steps)

        self.assertFalse(context.is_step_done('step01'))

        context.notify_step_done('step01')
        self.assertTrue(context.is_step_done('step01'))

    def test_notify_changes(self):
        context = SimpleContextManager()
        context.load('unittest', steps)

        context.notify_step_error('step03')
        self.assertEqual('ERROR', get_step_by_name(context.exec_map['steps'], 'step03')['status'])

        context.notify_step_running('flow01')
        self.assertEqual('RUNNING', get_step_by_name(context.exec_map['steps'], 'flow01')['status'])
        self.assertIsNotNone(get_step_by_name(context.exec_map['steps'], 'flow01')['start_at'])

        context.notify_step_done('step01')
        self.assertEqual('DONE', get_step_by_name(context.exec_map['steps'], 'step01')['status'])
        self.assertIsNotNone(get_step_by_name(context.exec_map['steps'], 'step01')['end_at'])

    def test_notify_batch_done(self):
        context = SimpleContextManager()
        context.load('unittest', steps)

        context.notify_batch_done()

        self.assertEqual('complete', context.exec_map['status'])
        self.assertIsNotNone(context.exec_map['end_at'])

    def test_is_batch_complete(self):
        context = SimpleContextManager()
        context.load('unittest', steps)

        context.notify_batch_done()

        self.assertTrue(context.is_batch_complete())
