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


def get_request(url, decode=None):
    """Get some data using the API and the provided url."""
    response = requests.get(url)
    request_ok, status, msg = _check_status(response)
    data = None
    if request_ok:
        data = response.content
        if decode is not None:
            data = data.decode('utf-8')
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

    data = get_request(url, decode='utf-8')
    return data


def weathericon(symbol, image_type='png', night=False, polar_night=False,
                output_file=None):
    """Get a weather icon.

    Parameters
    ----------
    symbol : int
        The symbol we are to get.
    image_type : string, optional
        The format for the image to get. Valid types are "png", "svg"
        or "svg+xml".
    night : boolean, optional
        If True, we will get a moon symbol.
    polar_night : boolean, optional
        If True, we will get a polar night symbol.
    output_file : string, optional
        A file name which we will write the icon to.

    Returns
    -------
    image :
        The image dowloaded.

    See Also
    --------
    https://api.met.no/weatherapi/weathericon/_/documentation/

    """
    if image_type not in ('svg', 'png', 'svg+xml'):
        raise ValueError('Image type {} not supported!'.format(image_type))
    post_image_type = image_type
    if '+' in image_type:
        post_image_type = image_type.replace('+', '%2B')
    url = (
        '{base}/weathericon/1.1/?symbol={symbol}&'
        'content_type=image/{image_type}'
    ).format(
        base=API_URL,
        symbol=symbol,
        image_type=post_image_type,
    )
    if night and polar_night:
        raise ValueError(
            'The settings night and polar_night can not both be True!'
        )
    if night:
        url += '&is_night=1'
    if polar_night:
        url += '&is_polarnight=1'
    data = get_request(url)
    if output_file is not None:
        with open(output_file, 'wb') as output:
            output.write(data)
    return data
