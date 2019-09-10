import unittest
import datetime
from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.services import date_service 


class TestDates(unittest.TestCase):
    """
    Test the functions used by the PSU module
    """

    def test_date_strings(self):
        """
        Test the Date functions of psu_base
        """

        self.assertTrue(
            date_service.string_to_date("31-JAN-2018") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #1"
        )
        self.assertTrue(
            date_service.string_to_date("2018-01-31") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #2"
        )
        self.assertTrue(
            date_service.string_to_date("1/31/2018") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #3"
        )
        self.assertTrue(
            date_service.string_to_date("1/31/18") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #4"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #5"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30:45") == datetime.datetime(2018, 1, 31, 1, 30, 45, 0),
            "String-to_date #6"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30") == datetime.datetime(2018, 1, 31, 1, 30, 0),
            "String-to_date #7"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30 PM") == datetime.datetime(2018, 1, 31, 13, 30, 0),
            "String-to_date #8"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30 pm") == datetime.datetime(2018, 1, 31, 13, 30, 0),
            "String-to_date #9"
        )
        # An error message will be printed here. Suppress it.
        self.assertTrue(
            date_service.string_to_date("Today at 7:30") is None,
            "String-to_date #10"
        )

    def test_convenient_dates(self):
        """
        Test the ConvenientDate class
        """
        dd = ConvenientDate('01/31/2019')

        self.assertTrue(dd.datetime_instance, "ConvenientDate #1")
        self.assertTrue(dd.arrow_instance, "ConvenientDate #2")
        self.assertTrue(dd.banner_date() == "31-JAN-2019", "ConvenientDate #3")
        self.assertTrue(dd.date_field() == "2019-01-31", "ConvenientDate #4")
        self.assertTrue(dd.timestamp() == "2019-01-31 00:00:00", "ConvenientDate #5")

        dd = ConvenientDate('06/08/2019 15:37')

        self.assertTrue(dd.banner_date() == "08-JUN-2019", "ConvenientDate #6")
        self.assertTrue(dd.timestamp() == "2019-06-08 15:37:00", "ConvenientDate #7")


if __name__ == '__main__':
    unittest.main()
