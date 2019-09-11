"""Helper Functions"""


def checked_data_length(data, length):
    '''Check if data is a string and character length does not exceed the specified length.

    Parameters
    ----------
    data : str
        String data to be checked.
    length: int
        Specified maximum length of data.

    Returns
    -------
        Returns @param:data or None'''

    if type(length) != int:
        raise TypeError("Parameter length must be integer.")

    if data and type(data) == str and len(data) < length:
        return data

    return None
