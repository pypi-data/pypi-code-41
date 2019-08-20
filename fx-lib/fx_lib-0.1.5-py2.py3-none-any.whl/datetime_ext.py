from datetime import datetime, timedelta


__all__ = ["Date"]


class Date(datetime):

    def __new__(cls, dt=datetime.today()):
        if not isinstance(dt, datetime):
            raise TypeError("Wrong type. Should be Datetime")
        self = datetime.__new__(cls, dt.year, dt.month, dt.day)
        self._dt = dt
        return self

    def to_string_YYYY_MM_DD(self, delimiter="-"):
        f = "%Y{0}%m{0}%d".format(delimiter)
        return self._dt.strftime(f)

    def offset(self, days: int) -> datetime:
        """
        :param days:
        :return:
        """
        return self._dt + timedelta(days=days)

    def next_days(self, days: int) -> datetime:
        """
        :param days:
        :return:
        """
        if days <= 0:
            raise ValueError("Days could not be zero or negative. Current Value is: {}".format(days))
        return self.offset(days)

    def before_days(self, days: int) -> datetime:
        """
        :param days:
        :return:
        """
        if days <= 0:
            raise ValueError("Days could not be zero or negative. Current Value is: {}".format(days))
        return self.offset(-days)

    @staticmethod
    def today() -> datetime:
        return datetime.today()

    @staticmethod
    def yesterday() -> datetime:
        return Date(datetime.today()).before_days(1)
