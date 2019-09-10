import datetime
import pytz
import tzlocal
from dateutil.relativedelta import relativedelta
from parsedatetime import parsedatetime
import warnings


class ZeitzonoTime:
    """
    a time object
    - basically keeps a time (datetime.datetime) and a timezone
    - initalized with local time and local timezone
    - can update time with new time (will be treated as utc)

    """

    def __init__(self):
        self.time = self._get_utc_now()
        self.set_tz_local()

    def set_tz(self, tz):
        tz = self._tz_to_pytz(tz)
        self.time = self.time.astimezone(tz)

    def set_tz_local(self):
        localtz = self._get_local_tz()
        self.time = self.time.astimezone(localtz)

    def set_time_now(self):
        tz = self.get_tz()
        self.time = self._get_utc_now().astimezone(tz)

    def set_time_nlp(self, englishtime):

        pdt_consts = parsedatetime.Constants()
        pdt_cal = parsedatetime.Calendar(pdt_consts)
        tzinfo = self.time.tzinfo
        parsed_dtresult, errno = pdt_cal.parseDT(englishtime, tzinfo=tzinfo)

        if errno == 0:
            return False

        # mk = time.mktime(result)
        # result_dt = datetime.datetime.fromtimestamp(mk)
        # self.time = result_dt.astimezone(curr_tz)
        self.time = parsed_dtresult
        return True

    def get_time_utc(self):
        return self.time.astimezone(pytz.utc)

    def get_time(self):
        return self.time

    def get_time_str(self):
        return self._time_to_str(self.time)

    def get_tz(self):
        return self.time.tzinfo

    def get_time_tz_str(self, tz):
        return self._time_to_str(self.get_time_tz(tz))

    def get_time_tz(self, tz):
        return self.time.astimezone(self._tz_to_pytz(tz))

    def zero_sec(self):
        self.time = self.time.replace(second=0)

    def zero_min(self):
        self.time = self.time.replace(minute=0)

    def add_sec(self):
        self.time = self.time + datetime.timedelta(seconds=1)

    def sub_sec(self):
        self.time = self.time - datetime.timedelta(seconds=1)

    def add_min(self):
        self.time = self.time + datetime.timedelta(seconds=60)

    def sub_min(self):
        self.time = self.time - datetime.timedelta(seconds=60)

    def add_hour(self):
        self.time = self.time + datetime.timedelta(seconds=3600)

    def sub_hour(self):
        self.time = self.time - datetime.timedelta(seconds=3600)

    def add_qhour(self):
        self.time = self.time + datetime.timedelta(seconds=900)

    def sub_qhour(self):
        self.time = self.time - datetime.timedelta(seconds=900)

    def add_day(self):
        self.time = self.time + datetime.timedelta(days=1)

    def sub_day(self):
        self.time = self.time - datetime.timedelta(days=1)

    def add_qday(self):
        self.time = self.time + datetime.timedelta(hours=6)

    def sub_qday(self):
        self.time = self.time - datetime.timedelta(hours=6)

    def add_week(self):
        self.time = self.time + datetime.timedelta(days=7)

    def sub_week(self):
        self.time = self.time - datetime.timedelta(days=7)

    def add_month(self):
        self.time = self.time + relativedelta(months=1)

    def sub_month(self):
        self.time = self.time - relativedelta(months=1)

    def add_year(self):
        self.time = self.time + relativedelta(years=1)

    def sub_year(self):
        self.time = self.time - relativedelta(years=1)

    def __str__(self):
        return self._time_to_str(self.time)

    def _time_to_str(self, time):
        return time.strftime("%a") + " " + str(time)

    def _get_utc_now(self):
        now = datetime.datetime.utcnow()
        now = now.replace(microsecond=0)
        nowutc = now.replace(tzinfo=pytz.utc)
        return nowutc

    def _get_local_tz(self):

        # if tzlocal.get_localzone() cannot determine the local machine's time
        # zone, it returns UTC, but throws a warning
        #
        # we want to handle the warning gracefully, so we convert it to an
        # exception and catch it and return UTC ourselves

        warnings.simplefilter("error")

        try:
            localzone = tzlocal.get_localzone()
        except UserWarning:
            return pytz.utc

        return localzone

    def _tz_to_pytz(self, tz):
        if isinstance(tz, str):
            return pytz.timezone(tz)
        else:
            return tz
