import nose2.events
import unittest

__unittest = True

class ResultReporter(nose2.events.Plugin):
    """Result plugin that just prints the test ids"""
    alwaysOn = True

    def __init__(self):
        self.tests = []

    def startTest(self, event):
        event.handled = True
        if not issubclass(event.test.__class__, Exception):
            test = event.test.id().split()[0]
            if 'FunctionTestCase' in type(event.test).__name__:
                test = "{}.{}".format(event.test.__module__, test)
            self.tests.append(test)

    def afterTestRun(self, event):
        self.tests.sort()
        for t in self.tests:
            print(t)
