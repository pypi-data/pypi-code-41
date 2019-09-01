# Copyright (c) 2019, Anders Lervik.
# Distributed under the MIT License. See LICENSE for more info.
"""A module for interfacing the MET Norway Weather API."""
import requests


API_URL = 'https://api.met.no/weatherapi'


STATUS = {
    200: 'OK',
    203: 'Non-Authorative Information - deprecated product version',
    304: 'Not Modified',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'No data from the product handler',
    422: 'Unprocessable Entity',
    429: 'Too Many Requests',
    499: 'Client Closed Request',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Time-out',
}


def _check_status(response):
    """Check the status of a requests response."""
    status = response.status_code
    if status in STATUS:
        return status == 200, status, STATUS[status]
    return False, status, response.content


def get_request(url):
    """Get some data using the API and the provided url."""
    response = requests.get(url)
    request_ok, status, msg = _check_status(response)
    data = None
    if request_ok:
        data = response.content.decode('utf-8')
    else:
        print('Could not get data:')
        print('Status: {}'.format(status))
        print('MSG: {}'.format(msg))
    return data


def location_forecast(lat, lon, msl=None):
    """Get a location forecast for the given lat, lon location.

    Parameters
    ----------
    lat : float
        The latitude to get the forecast for.
    lon : float
        The longitude to get the forecast for.
    msl : float
        The height above sea level to get the forecast for.

    Returns
    -------
    data : string
        The raw data (xml) containing the forecast.

    See Also
    --------
    https://api.met.no/weatherapi/locationforecast/1.9/documentation

    """
    url = '{base}/locationforecast/1.9/?lat={lat}&lon={lon}'.format(
        base=API_URL,
        lat=lat,
        lon=lon
    )
    if msl is not None:
        url += '&msg={msl}'.format(msl=msl)

    data = get_request(url)
    return data
