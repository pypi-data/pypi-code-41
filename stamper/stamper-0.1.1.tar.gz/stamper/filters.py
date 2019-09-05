
import re
from datetime import datetime, date, timedelta


class DateFilter(object):

    """
    Filtering tools for the dates input provided by the user
    """

    def __init__(self, date_format):
        self.date_format = date_format

    def days(self, current_date, days, action='-'):
        """
        Add/substract the given number of days from the given current_date
        """
        delta = timedelta(days=days)
        if action == '-':
            new_date = current_date - delta
        else:
            new_date = current_date + delta
        new_date = new_date.replace(hour=0, minute=0, second=0)
        return new_date

    def days_ago(self, current_date, days):
        """
        Return the date N days ago from the current date
        """
        return self.days(current_date, days, '-')

    def days_future(self, current_date, days):
        """
        Return the date N days in the future from the current date
        """
        return self.days(current_date, days, '+')

    def months(self, current_date, months, action='-'):
        """
        Add/substract the given number of months from the given current_date
        """
        if action == '-':
            # start travelling in time, back to N months ago
            for n in range(months):
                current_date = current_date.replace(day=1) - timedelta(days=1)
        else:
            # start travelling in time, forward to N months
            for n in range(months):
                current_date = current_date.replace(day=1) + timedelta(days=1)

        # Now use the new year/month values + the current day to set the proper
        # date
        new_date = datetime(
            current_date.year, current_date.month, date.today().day)
        return new_date

    def months_ago(self, current_date, months):
        """
        Return the date N days ago from the current date
        """
        return self.months(current_date, months, '-')

    def months_future(self, current_date, months):
        """
        Return the date N days in the future from the current date
        """
        return self.months(current_date, months, '+')

    def parse_number_filter(self, number_filter, start_date=None,
                            future=False):
        """
        Given a numeric filter with the N[d|w|m|y] pattern, return both
        the number of days/months/years that apply as a filter, + the
        date N[d|w|m|y] ago from start_date (which defaults to today if
        None is passed).

        If future is True, it will return a date in the future, not from
        the past.
        """
        number = None
        filtered_date = None
        start_date = start_date or datetime.today()

        # set which methods use to process the date, going backwards into the
        # past as a default, unless we are told otherwise
        filter_days = self.days_ago
        filter_months = self.months_ago
        if future:
            filter_days = self.days_future
            filter_months = self.months_future

        if re.search(r'(\d+[dD]{1})', number_filter):
            number = int(number_filter.lower().replace('d', ''))
            filtered_date = filter_days(start_date, number)

        elif re.search(r'(\d+[wW]{1})', number_filter):
            number = int(number_filter.lower().replace('w', '')) * 7
            filtered_date = filter_days(start_date, number)

        elif re.search(r'(\d+[mM]{1})', number_filter):
            number = int(number_filter.lower().replace('m', ''))
            filtered_date = filter_months(start_date, number)

        elif re.search(r'(\d+[yY]{1})', number_filter):
            number = int(number_filter.lower().replace('y', ''))
            today = date.today()
            # by default assume going backwards into the past...
            year = today.year - number
            if future:
                #...unless told otherwise
                year = today.year + number
            filtered_date = datetime(year, today.month, today.day)

        return number, filtered_date

    def validate(self, stamp_filter):
        """
        Validate a given filter. Filters can have the following notation:

        - %Y-%m-%d: Times recorded at a given date

        - %Y-%m-%d--%Y-%m-%d: Times recorded between two dates

        - *%Y-%m-%d: Times recorded up to a  given date

        - %Y-%m-%d*: Times recorded from a given date

        - %Y-%m-%d+sN[d|w|m|y]: Times recorded since the given date up to
          N more days/weeks/months/years

        - N...N[d|w|m|y]: Times recorded N...N days/weeks/months/years ago

        Important: all date comparisons are made on datetime objects, using
        00:00 as the time (first second of the given day). This means that
        for range filters, the first day is included, but the second day is not
        """
        filter_from = None
        filter_to = None

        if stamp_filter is None:
            return filter_from, filter_to

        if '--' in stamp_filter:
            filter_from, filter_to = stamp_filter.split('--')
            filter_from = datetime.strptime(filter_from, self.date_format)
            filter_to = datetime.strptime(filter_to, self.date_format)

        elif stamp_filter.startswith('*'):
            filter_to = datetime.strptime(stamp_filter, '*'+self.date_format)
            filter_to = filter_to.replace(hour=0, minute=0, second=0)

        elif stamp_filter.endswith('*'):
            filter_from = datetime.strptime(stamp_filter, self.date_format+'*')
            filter_from = filter_from.replace(hour=0, minute=0, second=0)

        elif '+' in stamp_filter:
            # "+" filtering works with a date following by "+", a number and
            # a letter (d|w|m|y) which sets the number of days, weeks, months,
            # years we would like to go into the future
            filter_from, number = stamp_filter.split('+')
            filter_from = datetime.strptime(filter_from, self.date_format)
            number, filter_to = self.parse_number_filter(
                number, filter_from, future=True)

        elif stamp_filter.count('-') == 3:
            # "-" filtering works with a date followed by "-", a number and
            # a letter (d|w|m|y) which sets the number of days, weeks, months,
            # years we would like to go backwards into the past
            year, month, day, number = stamp_filter.split('-')
            filter_to = '-'.join([year, month, day])
            filter_to = datetime.strptime(filter_to, self.date_format)
            number, filter_from = self.parse_number_filter(number, filter_to)

        else:
            # Check if the user is asking for N days/weeks/months/years
            number, filter_from = self.parse_number_filter(stamp_filter)
            if number is None:
                # no filtering found, maybe they are giving us a fixed date
                try:
                    filter_from = datetime.strptime(stamp_filter,
                                                    self.date_format)
                except:
                    # nothing to be used as a filter, go on, printing a warning
                    print('[warning] invalid date filter: ' + stamp_filter)
                else:
                    filter_from = filter_from.replace(hour=0, minute=0,
                                                      second=0)
                    filter_to = filter_from + timedelta(days=1)

        return filter_from, filter_to
