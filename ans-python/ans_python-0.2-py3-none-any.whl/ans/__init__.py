from os import getenv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class AnsClient():
    """Ans client."""

    def __init__(self):
        """Initialise."""
        self.__email = getenv("ANS_EMAIL")
