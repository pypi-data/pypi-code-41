import base64
import os

import pandas as pd
import requests

from gerby.secrets import HARVEST_ACCOUNT_ID, HARVEST_TOKEN


class HarvestClient(object):
    """HarvestClient for interacting with harvest api v2.0"""

    base_url = "https://api.harvestapp.com/v2/"
    time_off_id = 16121361

    def __init__(self, token=HARVEST_TOKEN, account_id=HARVEST_ACCOUNT_ID):
        """
        Args:
            token (str): harvest api token
            account_id (int): harvest account id
        Returns:
            instance of harvest client
        """
        self.headers = {
            "accept": "application/json",
            "authorization": "Bearer " + token,
            "Harvest-Account-ID": account_id,
            "Content-Type": "application/json",
        }

    def _post(self, url, **kwargs):
        response = requests.post(
            self.base_url + url, headers=self.headers, params=kwargs
        )
        response.raise_for_status()
        return response.json()

    def _get(self, url, **kwargs):
        response = requests.get(
            self.base_url + url, headers=self.headers, params=kwargs
        )
        response.raise_for_status()
        return response.json()

    def users(self, **kwargs):
        """Invoices
        Kwargs:
            is_active
            updated_since
            page
            per_page
        """
        return self._get("users", **kwargs)

    def invoice(self, invoice_id):
        """Invoice
        Kwargs:
            invoice_id (required)
        """
        return self._get("invoices/" + str(invoice_id))

    def invoices(self, **kwargs):
        """Invoices
        Kwargs:
            is_active
            client_id
            updated_since
            page
            per_page
        """
        return self._get("invoices", **kwargs)

    def projects(self, **kwargs):
        """Projects
        Kwargs:
            is_active
            client_id
            updated_since
            page
            per_page
        """
        return self._get("projects", **kwargs)

    def clients(self, **kwargs):
        """Clients
        Kwargs:
            is_active
            updated_since
            page
            per_page
        """
        return self._get("clients", **kwargs)

    def user_project_assignments(self, project_id, **kwargs):
        """User Project Assignments
        Args:
            project_id
        Kwargs:
            updated_since
            page
            per_page
        """
        url = "projects/" + str(int(project_id)) + "/user_assignments"
        return self._get(url, **kwargs)

    def create_user_project_assignments(self, project_id, **kwargs):
        """User Project Assignments
        Args:
            project_id
        Kwargs:
            user_id
            is_active
            is_project_manager
            hourly_rate
            budget
        """
        url = "projects/" + str(int(project_id)) + "/user_assignments"
        return self._post(url, **kwargs)

    def time_entries(self, **kwargs):
        """Time Entries
        Kwargs:
            user_id
            client_id
            is_billed
            is_running
            updated_since
            from
            to
            page
            per_page
        """
        url = "time_entries"
        return self._get(url, **kwargs)

    def fetch_all(self, attribute_type, **kwargs):
        """Fetch All
        Returns the full collection of objects from the harvest api.
        Wraps each of the other methods on HarvestClient
        Args:
            attribute_type - harvest client method name, ex: clients -or- time_entries
        Kwargs:
            (any) - these are simply passed down to the method specified
        """

        ll = []
        page = 1
        while True:
            result = getattr(self, attribute_type)(page=page, **kwargs)
            page = page + 1
            ll.extend(result[attribute_type])
            if not result["next_page"]:
                break
        return ll
