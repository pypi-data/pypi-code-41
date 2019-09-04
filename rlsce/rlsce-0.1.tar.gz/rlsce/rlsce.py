from datetime import datetime
from datetime import timedelta
from sentry_sdk import capture_exception


class Sentry:
    date_exceptions = {}

    @staticmethod
    def send(function, exception):
        global date_exceptions

        date_exceptions[function] = datetime.now()
        capture_exception(exception)

    @staticmethod
    def send_exception(function, exception, minutes):
        global date_exceptions

        try:
            last_exception_date = date_exceptions[function]
            if last_exception_date <= (datetime.now() - timedelta(minutes=minutes)):
                Sentry.send(function, exception)

        except KeyError:
            Sentry.send(function, exception)
