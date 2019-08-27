# -*- encoding: utf-8 -*-


class DefaultSettings(object):
    """The default configuration of the GUI just demonstrates the available options."""
    TIMEZONE = "UTC"
    """
    A timezone is required to localise the display of the first seen/last
    seen timestamps
    """
    WOOHOO_APPLICATION_ROOT = ""
    """
    Set this to the subpath When the pDNS GUI is not running in the root of a
    vHost.
    """
    SECRET_KEY = "snakeoil"
    """Flask uses a secret key to encrypt things that sould be tamper proof (for example the Session object)."""
    API_KEY = "MsfPfDqYMQGDc4nVcGTMS8UA"
    """The API key used to access the pDNS database."""
    API_ENTRYPOINT = "http://localhost:5000/api"
    """The URL (entry point) to call for queries."""
