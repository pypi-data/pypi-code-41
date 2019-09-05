import os

from time_converter import Converter
import pandas as pd
import datetime as dt
import warnings

from time_converter.converters.spice_utilities import setup_spice, datetime_to_solarday_number, datetime_to_lst, \
    lst_to_datetime

try:
    import spiceypy as spice
except ImportError:
    spice = None

FIRST_LUNARDAY = dt.datetime(2018, 12, 22, 16, 25, 51, 600000)

CHANGE4_LONGITUDE = 177.6
# source: http://www.cnsa.gov.cn/english/n6465652/n6465653/c6805049/content.html


class Change4LocalTimeConverter(Converter):
    _data = None
    _day_cache = []

    def _load_data(self):
        warnings.warn('Using precomputed data for Chang\'E 4 local time calculation.\n'
                      'Run:\n'
                      'pip3 install --user time_converter[spice]\n'
                      'to use spiceypy for better accuracy and performance.')
        if self._data is not None:
            return self._data
        else:
            filename = os.path.join(os.path.dirname(__file__), 'change4_localtime.dat')
            data = pd.read_csv(filename, index_col=0, parse_dates=[0, 2])
            data['time'] = pd.Series([val.time() for val in data['time']], index=data.index)
            self._data = data
            return data

    def supports(self, unit=None, datatype=None):
        return (datatype is None or issubclass(datatype, tuple)) and (unit == 'ce4lst')

    def convert_from_datetime(self, datetime):
        if spice is not None:
            setup_spice()

            if datetime < FIRST_LUNARDAY:
                raise ValueError('unsupported date: {}'.format(datetime))

            day = datetime_to_solarday_number(datetime, FIRST_LUNARDAY, 'MOON', CHANGE4_LONGITUDE, self._day_cache)
            time = datetime_to_lst(datetime, 'MOON', CHANGE4_LONGITUDE)
            return day, time
        else:
            data = self._load_data()
            value = pd.Timestamp(datetime)

            if value > data.index.max() or value < data.index.min():
                raise ValueError('unsupported date: {}'.format(datetime))

            row = data.asof(value)
            return row['LD'], row['time']

    def convert_to_datetime(self, value):
        if spice is not None:
            setup_spice()
            if value[0] < 1:
                raise ValueError('unsupported lunar day: {}'.format(value[0]))

            return lst_to_datetime(value[0], value[1], FIRST_LUNARDAY, 'MOON', CHANGE4_LONGITUDE, self._day_cache)
        else:
            data = self._load_data()
            if value[0] < 1 or value[0] >= data['LD'].max():
                raise ValueError('unsupported lunar day: {}'.format(value[0]))

            masked_data = data[(data['LD'] == value[0]) & (data['time'] >= value[1])]
            if len(masked_data) == 0:
                masked_data = data[data['LD'] > value[0]]
            return pd.Timestamp(masked_data.index.values[0]).to_pydatetime()