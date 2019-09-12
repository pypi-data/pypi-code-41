from test.BaseTest import SaveValueStep
from batchflows.contextmanager.ContextManager import SimpleContextManager
import unittest

steps = [
    SaveValueStep(),
    SaveValueStep(required=True)
]


class StepTest(unittest.TestCase):
    def test_happy_start(self):
        cm = SimpleContextManager()
        cm.load('unit', steps)

        step = steps[0]
        step.start(cm)

        self.assertEqual(1, cm.context['some_value'])

    def test_step_already_done(self):
        step = steps[0]

        cm = SimpleContextManager()
        cm.load('unit', steps)
        cm.notify_step_done(step.name)

        step.start(cm)

        self.assertIsNone(cm.context.get('some_value'))

    def test_step_already_done_but_required(self):
        step = steps[1]

        cm = SimpleContextManager()
        cm.load('unit', steps)
        cm.notify_step_done(step.name)

        step.start(cm)

        self.assertEqual(1, cm.context['some_value'])
