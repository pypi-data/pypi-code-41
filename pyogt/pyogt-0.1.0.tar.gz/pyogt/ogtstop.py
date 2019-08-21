"""Class to represent a stop from the OGT rest api."""


class OGTStop(object):
    """Class to store information about a stop."""

    def __init__(self, name='', id_=-1, pretty_name=''):
        """Initialize an OGTStop."""
        self._name = name
        self._id = id_
        self._pretty_name = pretty_name

    def get_name(self):
        """Return the name of the stop."""
        return self._name

    def get_id(self):
        """Return the id of the stop."""
        return self._id

    def get_pretty_name(self):
        """Return the pretty name of the stop."""
        return self._pretty_name
