import nose2.events

__unittest = True

class ResultReporter(nose2.events.Plugin):
    """Result plugin that just prints the test ids"""
    alwaysOn = True

    def __init__(self):
        self.tests = []

    def startTest(self, event):
        event.handled = True
        if not issubclass(event.test.__class__, Exception):
            self.tests.append(event.test.id().split()[0])

    def afterTestRun(self, event):
        self.tests.sort()
        for t in self.tests:
            print(t)
