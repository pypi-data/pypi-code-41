import os

import requests
from cached_property import cached_property

from gerby.secrets import FORECAST_ACCOUNT_ID, FORECAST_TOKEN


class ForecastClient:

    base_url = "https://api.forecastapp.com/"
    time_off_id = 3241

    def __init__(self, account_id=FORECAST_ACCOUNT_ID, token=FORECAST_TOKEN):

        self.headers = {
            "accept": "application/json",
            "authorization": "Bearer " + token,
            "Forecast-Account-ID": account_id,
            "Content-Type": "application/json",
        }

        if "error" in self.whoami():
            raise Exception("Forecast not authed")

    @cached_property
    def projects(self):
        return self.get_projects()["projects"]

    @cached_property
    def clients(self):
        return self.get_clients()["clients"]

    @cached_property
    def people(self):
        return self.get_people()["people"]

    def __parse_response(self, r):
        if r.status_code > 400:
            return {"error": r.json()}
        else:
            return r.json()

    def __get(self, url):
        return self.__parse_response(
            requests.get(self.base_url + url, headers=self.headers)
        )

    def whoami(self):
        return self.__get("whoami")

    def get_projects(self):
        return self.__get("projects")

    def get_clients(self):
        return self.__get("clients")

    def get_people(self):
        return self.__get("people")

    def assignments(self, start_date, end_date):
        url = f"assignments?end_date={end_date}&start_date={start_date}&state=active"
        return self.__get(url)
