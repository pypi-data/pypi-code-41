import spiceypy as spice
import datetime as dt
import math
import pandas as pd

SPICE_KERNELS_PATH = '/home/asterix/forstner/git/spiceminer/data'

spice.furnsh('{}/base/spk/planets/de430.bsp'.format(SPICE_KERNELS_PATH))
spice.furnsh('{}/base/lsk/naif0011.tls'.format(SPICE_KERNELS_PATH))
spice.furnsh('{}/base/pck/pck00010.tpc'.format(SPICE_KERNELS_PATH))

CHANGE4_LONGITUDE = 177.6
# source: http://www.cnsa.gov.cn/english/n6465652/n6465653/c6805049/content.html

moon = spice.bodn2c('MOON')


def get_localtime(time, body, lon):
    h, m, s, _, _ = spice.et2lst(spice.datetime2et(time), body, lon, 'PLANETOCENTRIC')
    return dt.time(h, m, s)


def get_change4_localtime(time):
    return get_localtime(time, moon, math.radians(177.6))

if __name__ == '__main__':
    index = pd.date_range(freq='30min', start=dt.datetime(2018, 12, 22, 16), end=dt.datetime(2022, 1, 1))
    localtimes = pd.Series([get_change4_localtime(val) for val in index], index=index)

    datetimes = pd.Series([dt.datetime.combine(dt.date(2019, 1, 1), val) for val in localtimes], index=index)
    new_lunar_day = datetimes.diff() < dt.timedelta(seconds=0)
    lunar_days = pd.Series([new_lunar_day[:val].sum() for val in index], index=index)

    df = pd.DataFrame({'LD': lunar_days, 'time': localtimes}, index=index)
    df.to_csv('converters/change4/change4_localtime.dat')
