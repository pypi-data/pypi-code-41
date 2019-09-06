
import gspread
from json import load
from logging import getLogger
from os import environ
from oauth2client.service_account import ServiceAccountCredentials
from re import sub
import socket
from pyux.time import Timer


class Gspread:
    """Google spreadsheet handler

    :param name: name of spreadsheet to connect to
    :param environ_prefix: prefix of environment variables containing credits
    :param credentials: path to json containing credentials
    
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
        """Open a worksheet and set it in self.sheets dictionary"""
        self.sheets[title] = gspread.authorize(self.credentials).open(self.name).worksheet(title)
        return self
    
    def append_row(self, worksheet: str, item: list):
        """Append a row to a worksheet"""
        self.sheets[worksheet].append_row(values = item)
        return self
    
    def read_records(self, worksheet: str) -> list:
        """Return records from a worksheet, as a list"""
        return self.sheets[worksheet].get_all_records()
    
    def delete_records(self, worksheet: str, rows: int = 1):
        """Delete records by resizing a worksheet"""
        self.sheets[worksheet].resize(rows = rows)
        return self


class NetworkWait:
    """Ping google.com to see if an internet connection is available"""
    def __init__(self, delay: int = 10, hostname: str = 'www.google.com'):
        self.connected = False
        self.stubborn_ping(delay = delay, hostname = hostname)
    
    def ping(self, hostname: str) -> None:
        try:
            # see if we can resolve the host name -- tells us if there is a DNS listening
            host = socket.gethostbyname(hostname)
            # connect to the host -- tells us if the host is actually reachable
            socket.create_connection((host, 80), 2)
        except Exception:
            self.connected = False
        else:
            self.connected = True
        return
    
    def stubborn_ping(self, delay: int, hostname: str) -> None:
        logger = getLogger(__name__)
        while not self.connected:
            self.ping(hostname = hostname)
            if not self.connected:
                Timer(delay = delay, message = 'No connection to internet, wait then try again')
        logger.info('Internet connection tested and ready to go.')
        return
