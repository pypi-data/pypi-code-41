import json


def load_json(data):
    """
    Loads a JSON string and returns the dictionary.

    Parameters
    ----------
    data : str or bytes
        If the input data is not as tring but bytes, it will automatically
        be converted to string before parsing the JSON.

    Returns
    -------
    dict
        The parsed JSON.
    """
    try:
        return json.loads(data)
    except TypeError:
        # Decode bytes into string
        return json.loads(data.decode())
