import math
import datetime as dt
import dateutil.parser
import numpy as np
import os
from tqdm import tqdm
import requests

try:
    import spiceypy as spice
except ImportError:
    spice = None


def download_file(url, filename):
    r = requests.get(url, stream=True)
    size = int(r.headers.get('content-length', 0))
    block_size = 8 * 1024
    with open(filename, 'wb') as file:
        pbar = tqdm(total=size, unit='B', unit_scale=True,
                    desc='downloading {}'.format(url.split('/')[-1]))
        for chunk in r.iter_content(block_size):
            file.write(chunk)
            pbar.update(len(chunk))
        pbar.close()


def setup_spice():
    if spice.ktotal('all') > 0: return

    SPICE_KERNELS_PATH = os.path.join(os.path.expanduser('~'), '.time_converter', 'spicefiles')
    os.makedirs(SPICE_KERNELS_PATH, exist_ok=True)

    for url in ['https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp',
                'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0011.tls',
                'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00010.tpc']:
        path = os.path.join(SPICE_KERNELS_PATH, url.split('/')[-1])
        if not os.path.isfile(path):
            download_file(url, path)
        spice.furnsh(path)


def datetime_to_solarday_number(date, startdate, body, longitude, day_cache=None):
    """
    Calculates the number of solar days that have passed since a certain date for an observer on a certain planet.

    :param date: Current date
    :param startdate: Starting date (e.g. date of landing)
    :param body: Solar system body on which the observer is located
    :param longitude: Longitude of the observer location on that planet
    """
    if day_cache is None:
        day_cache = []

    if len(day_cache) == 0 or day_cache[-1] < date:
        interval = spice.Cell_Double(2)
        begindate = startdate if len(day_cache) == 0 else day_cache[-1]
        spice.wninsd(spice.datetime2et(begindate), spice.datetime2et(date + dt.timedelta(days=60)), interval)
        result = spice.gfposc('SUN', 'IAU_{}'.format(body), 'NONE', body, 'LATITUDINAL', 'LONGITUDE',
                              '=', math.radians(longitude + 180), 0, 60, 750, interval)
        for i in range(0, len(result), 2):
            day_cache.append(et2datetime(result[i]))

    return np.searchsorted(np.array(day_cache), date) + 1


def et2datetime(et):
    return dateutil.parser.parse(spice.et2utc(et, 'ISOC', 1) + 'Z').replace(tzinfo=None)


def datetime_to_lst(date, body, longitude):
    h, m, s, _, _ = spice.et2lst(spice.datetime2et(date), spice.bodn2c(body), math.radians(longitude), 'PLANETOCENTRIC')
    return dt.time(h, m, s)


def lst_to_datetime(solarday, lst, startdate, body, longitude, day_cache=None):
    if solarday == 1 and lst < dt.time(0, 0, 1): return startdate

    if day_cache is None:
        day_cache = []

    if len(day_cache) < solarday:
        interval = spice.Cell_Double(2)
        begindate = startdate if len(day_cache) == 0 else day_cache[-1]
        spice.wninsd(spice.datetime2et(begindate),
                     spice.datetime2et(begindate + dt.timedelta(days=30) * (solarday - len(day_cache))), interval)
        result = spice.gfposc('SUN', 'IAU_{}'.format(body), 'NONE', body, 'LATITUDINAL', 'LONGITUDE',
                              '=', math.radians(longitude + 180), 0, 60, 750, interval)
        for i in range(0, len(result), 2):
            day_cache.append(dateutil.parser.parse(spice.et2utc(result[i], 'ISOC', 1) + 'Z').replace(tzinfo=None))

    angle = longitude + 180 - (lst.hour * 3600 + lst.minute * 60 + lst.second) / 86400 * 360

    interval = spice.Cell_Double(2)
    begindate = day_cache[solarday - 2] if solarday > 1 else startdate
    spice.wninsd(spice.datetime2et(begindate), spice.datetime2et(day_cache[solarday - 1]), interval)
    result = spice.gfposc('SUN', 'IAU_{}'.format(body), 'NONE', body, 'LATITUDINAL', 'LONGITUDE',
                          '=', math.radians(angle), 0, 60, 750, interval)
    return et2datetime(result[0])