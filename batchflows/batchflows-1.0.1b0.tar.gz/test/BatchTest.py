import logging
import unittest

from batchflows.Batch import Batch
from test.BaseTest import SaveValueStep, SumCalculatorStep


class BatchTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.ERROR)

    def test_happy_path_batch(self):
        batch = Batch()
        batch.add_step(SaveValueStep(value_name='value01'))
        batch.add_step(SaveValueStep(value_name='value02'))
        batch.add_step(SumCalculatorStep())
        batch.execute()

        self.assertEqual(2, batch.context['result'])

    def test_add_to_context(self):
        batch = Batch()
        batch.add_to_context('number', 12)
        batch.add_step(SaveValueStep(value_name='value01'))
        batch.add_step(SumCalculatorStep(attrs=('value01', 'number')))
        batch.execute()

        self.assertEqual(13, batch.context['result'])
