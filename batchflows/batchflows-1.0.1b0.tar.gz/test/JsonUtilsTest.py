from batchflows.util.JsonUtils import DateTimeDecoder, DateTimeEncoder, matches_datetime_pattern
from datetime import datetime
import unittest
import json


class FileContextManagerTest(unittest.TestCase):
    def test_parse_datetime_json(self):
        time = '2019-09-02T00:18:57.810341'
        value = {
            'some_date': datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')
        }

        str_json = json.dumps(value, cls=DateTimeEncoder)

        self.assertTrue(time in str_json)

    def test_matches_datetime_pattern(self):
        str_datetime = '2019-09-02T00:18:57.810341'
        var = matches_datetime_pattern(str_datetime)

        self.assertTrue(var)

    def test_load_date_time(self):
        str_datetime = '2019-09-02T00:18:57.810341'
        date = datetime.strptime(str_datetime, '%Y-%m-%dT%H:%M:%S.%f')

        value = {
            'some_date': date
        }

        str_json = json.dumps(value, cls=DateTimeEncoder)
        loaded = json.loads(str_json, cls=DateTimeDecoder)

        self.assertEqual(date, loaded['some_date'])
