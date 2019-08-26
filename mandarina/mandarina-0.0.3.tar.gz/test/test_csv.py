from mandarina.csv import *
import unittest
import random
import datetime


class CsvTests(unittest.TestCase):
    def test(self):
        pass

    def test_is_date_in_last_line(self):
        todays_date = str(datetime.datetime.now().date())
        with open("test.csv", "w") as filehandle:
            filehandle.write(str(datetime.datetime.now()) + "\n")
        self.assertTrue(day_is_already_written(todays_date, "test.csv"))
        delete_file("test.csv")

    def test_delete_last_line(self):
        random_int = random.randint(0,10)
        with open("test.csv", "w") as filehandle:
            for i in range(random_int):
                filehandle.write(str(datetime.datetime.now()) + "\n")

        delete_last_line("test.csv")
        self.assertEqual(random_int - 1, count_lines("test.csv"))
        delete_file("test.csv")

    def test_create_headers(self):
        header_line = "This,is,a,test"
        create_headers("test_header.csv", header_line)
        with open("test_header.csv") as f:
            first_line = f.readline().strip()
        self.assertEqual(first_line, header_line)
        delete_file("test_header.csv")

    def test_count_lines(self):
        random_int = random.randint(1, 10 ** 6)
        with open("test.csv", "w") as filehandle:
            for i in range(random_int):
                filehandle.write(str(datetime.datetime.now()) + "\n")
        self.assertEqual(count_lines("test.csv"), random_int)
        delete_file("test.csv")
