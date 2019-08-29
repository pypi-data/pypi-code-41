"""Ans Client."""

from os import getenv
from time import time
from dotenv import load_dotenv, find_dotenv
from requests import post, get

load_dotenv(find_dotenv())

ENDPOINT_HOST = 'https://secure.ans-delft.nl'
ENDPOINT_PATH = '/api/v1'


class AnsClient():
    """Ans client."""

    def __init__(self):
        """Initialise."""
        self.__email = getenv("ANS_EMAIL")
        self.__password = getenv("ANS_PASSWORD")

        if not self.__email or not self.__password:
            raise Error('ANS_EMAIL or ANS_PASSWORD is not defined.')

        self.token = None
        self.sign_in_at = None

    def list_assignments(self, course_id):
        """List assignments of a course."""
        return self.__get("/courses", json={"course_id": course_id})

    def list_courses(self):
        """Get all courses."""
        return self.__get("/courses")

    def __get(self, endpoint, json=None):
        response = get(f"{ENDPOINT_HOST}{ENDPOINT_PATH}{endpoint}",
                       headers=self.__headers(),
                       json=json
                       )

        if response.ok:
            return response.json()

        return None

    def __headers(self):
        if not self.token or self.sign_in_at + 60 < time():
            self.sign_in_at = time()
            self.token = self.__sign_in()

        return {'Authorization': f"Token token={self.token}"}

    def __sign_in(self):
        response = post(f"{ENDPOINT_HOST}{ENDPOINT_PATH}/user/sign-in",
                        json={"email": self.__email,
                              "password": self.__password
                              },
                        )
        if response.ok:
            return response.json()['auth_token']

        raise Error('Error during login.')


class Error(Exception):
    """Login error."""

    def __init__(self, message):
        """Initialise error."""
        self.message = message
