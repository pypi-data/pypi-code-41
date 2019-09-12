import logging
import unittest

from batchflows.Batch import ParallelFlows, Batch
from batchflows.CustomExceptions import ParallelFlowsException
from test.BaseTest import SaveValueStep, LazySumStep, TestSaveProgressContextManager


class ParallelFlowsTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.ERROR)

    def test_happy_path(self):
        cm = TestSaveProgressContextManager()
        batch = Batch(context_manager=cm)

        lazy_flow = ParallelFlows('LazyAsync')
        lazy_flow.add_step(SaveValueStep('Step01', 'some', 10))
        lazy_flow.add_step(SaveValueStep('Step02', 'some2', 12))

        batch.add_step(lazy_flow)
        batch.execute()

        self.assertEqual(10, batch.context['some'])
        self.assertEqual(12, batch.context['some2'])
        self.assertTrue(batch.context['save_progress_exec'])

    def test_lazy_happy_path_batch(self):
        batch = Batch()
        batch.context_manager.context = {
            'value01': 1,
            'value02': 2,
            'value03': 3
        }

        lazy_flow = ParallelFlows('LazyAsync')
        lazy_flow.add_step(LazySumStep(attrs=('value01', 'value02'), result_name='lazy01'))
        lazy_flow.add_step(LazySumStep(attrs=('value01', 'value03'), result_name='lazy02'))
        lazy_flow.add_step(LazySumStep(attrs=('value02', 'value03'), result_name='lazy03'))

        batch.add_step(lazy_flow)
        batch.execute()

        self.assertEqual(3, batch.context_manager.context['lazy01'])
        self.assertEqual(4, batch.context_manager.context['lazy02'])
        self.assertEqual(5, batch.context_manager.context['lazy03'])

    def test_async_flow_exception(self):
        batch = Batch()
        batch.context_manager.context = {
            'value01': 1,
            'value02': 2
        }

        lazy_flow = ParallelFlows('LazyAsync')
        lazy_flow.add_step(LazySumStep(attrs=('value01', 'value03'), result_name='lazy02'))
        lazy_flow.add_step(LazySumStep(attrs=('value02', 'value03'), result_name='lazy03'))

        try:
            batch.add_step(lazy_flow)
            batch.execute()
        except Exception as error:
            if not isinstance(error, ParallelFlowsException):
                raise Exception('test_async_flow_exception fail')
