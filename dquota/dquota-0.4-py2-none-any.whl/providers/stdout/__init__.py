import sys

class DQuotNotificationProviderStdout:
    def send(self, input):
        sys.stdout.write(input)
        sys.stdout.flush()
