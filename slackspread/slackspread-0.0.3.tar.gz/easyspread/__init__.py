
import gspread
from json import load
from logging import getLogger
from os import environ
from oauth2client.service_account import ServiceAccountCredentials
from re import sub
import socket
from pyux.time import Timer


class Gspread:
    """Google spreadsheet handler.

    :param name: name of spreadsheet to connect to
    :type name: str
    :param environ_prefix: prefix of environment variables containing valid credits
    :type environ_prefix: str
    :param credentials: path to json containing credentials
    :type credentials: str
    
    :ivar credentials: valid credentials to manipulate a spreadsheet through the API
    :type credentials: dict
    :ivar name: attribute to store argument ``name`` (spreadsheet name)
    :type name: str
    :ivar sheets: stores the worksheets opened with ``self.open_worksheet()`` as
        a dict, with the worksheet's title as key
    :type sheets: dict
    
    Environment variables need to have the form ``PROJECT_<varname>`` ::
    
            PROJECT_ID
            PRIVATE_KEY_ID
            PRIVATE_KEY
            CLIENT_ID
            CLIENT_EMAIL
    """
    
    def __init__(self, name: str, environ_prefix: str, credentials: str):
        credentials = Gspread.get_credentials(prefix = environ_prefix, file = credentials)
        self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            keyfile_dict = credentials,
            scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )
        self.name = name
        self.sheets = dict()
        
    def __repr__(self):
        return "Gspread(name = %s)" % self.name
        
    @staticmethod
    def get_credentials(prefix: str, file: str):
        """Read private keys from environ and update json credentials"""
        with open(file, 'r') as f:
            credentials = load(f)
        environ_variables = (
            "PROJECT_ID",
            "PRIVATE_KEY_ID",
            "PRIVATE_KEY",
            "CLIENT_ID",
            "CLIENT_EMAIL",
        )
        for var in environ_variables:
            path_var = prefix + '_' + var
            read_var = sub(pattern = '\\\\n', repl = "\n", string = environ.get(path_var))
            credentials[var.lower()] = read_var
        return credentials
        
    def open_worksheet(self, title: str):
        """Open a worksheet and store it in ``self.sheets`` dictionary"""
        self.sheets[title] = gspread.authorize(self.credentials).open(self.name).worksheet(title)
        return self
    
    def append_row(self, worksheet: str, item: list):
        """Append a row to a worksheet.
        
        The method returns ``self`` so that calls to ``append_row`` can be chained.
        
        :param worksheet: worksheet to append row to
        :type worksheet: str
        :param item: values to append
        :type item: list
        """
        self.sheets[worksheet].append_row(values = item)
        return self
    
    def read_records(self, worksheet: str) -> list:
        """Return records from a worksheet.
        
        The method skips the header row."""
        return self.sheets[worksheet].get_all_records()
    
    def delete_records(self, worksheet: str, rows: int = 1):
        """Delete records by resizing a worksheet."""
        self.sheets[worksheet].resize(rows = rows)
        return self


class NetworkWait:
    """Wait (infinitely) for an internet connexion.
    
    :param delay: seconds between each ping trial
    :type delay: int
    :param hostname: default ``www.google.com`` : the hostname to ping
    :type hostname: str
    
    :ivar connected: indicates that a connexion was found
    :type connected: bool
    """
    def __init__(self, delay: int = 10, hostname: str = 'www.google.com'):
        self.connected = False
        self.stubborn_ping(delay = delay, hostname = hostname)
    
    @staticmethod
    def ping(hostname: str) -> bool:
        """Ping the hostname to see if an internet connexion is available."""
        try:
            # see if we can resolve the host name -- tells us if there is a DNS listening
            host = socket.gethostbyname(hostname)
            # connect to the host -- tells us if the host is actually reachable
            socket.create_connection((host, 80), 2)
        except Exception:
            connected = False
        else:
            connected = True
        return connected
    
    def stubborn_ping(self, delay: int, hostname: str) -> None:
        """Ping every ``delay`` seconds until a connexion is found."""
        logger = getLogger(__name__)
        while not self.connected:
            self.connected = NetworkWait.ping(hostname = hostname)
            if not self.connected:
                Timer(delay = delay, message = 'No connection to internet, wait then try again')
        logger.info('Internet connection tested and ready to go.')
        return
