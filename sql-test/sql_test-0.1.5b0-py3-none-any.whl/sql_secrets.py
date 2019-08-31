"""
Store database password and other secrets.
THIS SHOULD BE PERSONALIZED AFTER INSTALLATION.
"""
from getpass import getpass

PASSWORD = getpass('Enter your password: ')
