import os
import requests
import glog as log
import pandas as pd
from io import BytesIO, BufferedReader
import numbers
from time import sleep
from zipfile import ZipFile


class FigureEightAPI:
    """An abstract class for all Figure Eight APIs.

    Attributes:
        _api_key (str): The API key that this API is using.
        _params (tuple): Default params for any Figure Eight API requests.
        _base_endpoint (str): The base endpoint for all Figure Eight APIs.

    """
    def __init__(self, api_key):
        """Create a FigureEightAPI.

        Args:
            api_key (str): Your Figure Eight API key.

        """
        log.debug("Creating FigureEightAPI")
        assert(isinstance(api_key, str))
        self._api_key = api_key
        self._params = (
            ("key", self._api_key),
        )
        self._base_endpoint = "https://api.figure-eight.com/v1/jobs"

    def _check_success(self, resp, error_message=None, success=200):
        """A hidden method to check if the response from a Figure Eight request
        was successful.

        Args:
            resp (requests.Response): The response object from a requests
                                      request.
            error_message (str, optional): A description of the error, if the request
                                           failed. Default: ""
            success (int, optional): The anticipated success code. Default: 200

        Raises:
            requests.exceptions.HTTPError: If `resp.status_code` is not equal
                                           to `success`

        """
        if error_message is None:
            error_message = ""

        if not isinstance(error_message, str):
            error_message = str(error_message)

        if not error_message.endswith(" "):
            error_message += " "

        error_message += f"Status Code: {resp.status_code}"

        if resp.status_code != success:
            log.error(error_message)
            raise requests.exceptions.HTTPError(error_message)


class FigureEightJob(FigureEightAPI):
    """A representation of a Figure Eight Job."""

    def __init__(self, api_key, job_id):
        """

        Args:
            api_key (str): Your Figure Eight API key.
            job_id (str, int): The Figure Eight Job's ID.

        """
        super().__init__(api_key)
        self._job_id = job_id
        self._figure_eight_json = None

    @property
    def figure_eight_json(self):
        """Get Figure Eight's Representation of the job.

        Returns:
            dict: Figure Eight's Representation of the job.

        """
        if self._figure_eight_json is None:
            resp = requests.get(f"{self._base_endpoint}/{self._job_id}.json",
                                params=self._params)
            self._check_success(resp, f"Failed to get job {self._job_id}.")
            self._figure_eight_json = resp.json()

        return self._figure_eight_json

    def _update_parameter_data(self, data, *parameters):
        """A method for updating most parts of the Figure Eight Job json.

        Args:
            data (str): The new value to update to in the Figure Eight json.
            *parameters (str): The field in the Figure Eight json to update.
                               Multiple fields implies depth in the json.

        Reference:
            https://success.figure-eight.com/hc/en-us/articles/202703425-Figure-Eight-API-Requests-Guide

        """
        assert(all(isinstance(parameter, str) for parameter in parameters))
        assert(isinstance(data, str))
        endpoint = f"{self._base_endpoint}/{self._job_id}.json"

        params = "".join([f"[{p}]" for p in parameters])
        params = (
            *self._params,
            (f"job{params}", data)
        )
        resp = requests.put(endpoint, params)
        self._check_success(resp, (f"Failed to update {parameters}"
                                   f" for job {self._job_id}."))

    class __reset_figure_eight_job_json:
        def __init__(self, f):
            self.f = f

        def __call__(self, inst, *args, **kwargs):
            inst._figure_eight_json = None
            return self.f(inst, *args, **kwargs)

    @property
    def title(self):
        """str: The title of the job."""
        return self.figure_eight_json["title"]

    @title.setter
    @__reset_figure_eight_job_json
    def title(self, title):
        self._update_parameter_data(title, "title")

    @property
    def instructions(self):
        """str: The instructions html of the job."""
        return self.figure_eight_json["instructions"]

    @instructions.setter
    @__reset_figure_eight_job_json
    def instructions(self, instructions):
        assert(isinstance(instructions, str))
        self._update_parameter_data(instructions, "instructions")

    @property
    def cml(self):
        """str: The Custom Markup Language task template for the job."""
        return self.figure_eight_json["cml"]

    @cml.setter
    @__reset_figure_eight_job_json
    def cml(self, cml):
        assert(isinstance(cml, str))
        self._update_parameter_data(cml, "cml")

    @property
    def payment_cents(self):
        """float: The amount paid to annotators per unit/row completed."""
        return self.figure_eight_json["payment_cents"]

    @payment_cents.setter
    @__reset_figure_eight_job_json
    def payment_cents(self, payment_cents):
        assert(isinstance(payment_cents, numbers.Number))
        self._update_parameter_data(payment_cents, "payment_cents")

    @property
    def judgments_per_unit(self):
        """int: The number of annotatorions required, per unit/row."""
        return self.figure_eight_json["judgments_per_unit"]

    @judgments_per_unit.setter
    @__reset_figure_eight_job_json
    def judgments_per_unit(self, judgments_per_unit):
        assert(isinstance(judgments_per_unit, numbers.Number))
        self._update_parameter_data(judgments_per_unit, "judgments_per_unit")

    @property
    def req_ttl_in_seconds(self):
        """float: The number of seconds per page/assignment."""
        return self.figure_eight_json["options"]["req_ttl_in_seconds"]

    @req_ttl_in_seconds.setter
    @__reset_figure_eight_job_json
    def req_ttl_in_seconds(self, req_ttl_in_seconds):
        assert(isinstance(req_ttl_in_seconds, numbers.Number))
        self._update_parameter_data(req_ttl_in_seconds,
                                    "options",
                                    "req_ttl_in_seconds")

    @property
    def units_per_assignment(self):
        """int: The number of units/rows per page/assignment."""
        return self.figure_eight_json["units_per_assignment"]

    @units_per_assignment.setter
    @__reset_figure_eight_job_json
    def units_per_assignment(self, units_per_assignment):
        assert(isinstance(units_per_assignment, numbers.Number))
        self._update_parameter_data(units_per_assignment,
                                    "units_per_assignment")

    @property
    def auto_launch(self):
        """bool: Whether auto-launch is enabled."""
        return self.figure_eight_json["auto_order"]

    @auto_launch.setter
    @__reset_figure_eight_job_json
    def auto_launch(self, auto_launch):
        assert(isinstance(auto_launch, numbers.Number))
        self._update_parameter_data(auto_launch, "auto_order")

    @property
    def id(self):
        """int: The job id."""
        return self._job_id

    @property
    def status(self):
        """dict: The number of units/rows by whether they've been completed or
                 not.

        To Do:
            Add logic and return a string (i.e. In Progess, Complete, etc.)
        """
        endpoint = f"{self._base_endpoint}/{self.id}/ping.json"

        resp = requests.get(endpoint, params=self._params)
        self._check_success(resp)

        return resp.json()

    def upload_csv(self, csv):
        """Upload units/rows to Figure Eight job.

        Args:
            csv (str, pandas.Dataframe): A local path or a remote url to a csv,
                                         or a pandas.DataFrame.

        """
        name = "sample.csv"
        if isinstance(csv, str) and os.path.exists(csv):
            name = csv
            csv = pd.read_csv(csv)

        assert(isinstance(csv, pd.DataFrame))
        endpoint = f"{self._base_endpoint}/{self.id}/upload.json"
        headers = {
            "Content-Type": "text/csv"
        }

        params = (
            *self._params,
            ("force", True)
        )

        filelike = BytesIO(csv.to_csv(index=False).encode())
        filelike.name = name
        resp = requests.put(endpoint,
                            headers=headers,
                            params=params,
                            data=BufferedReader(filelike))

        self._check_success(resp)

    def pause(self):
        """Pause the Figure Eight job."""
        endpoint = f"{self._base_endpoint}/{self.id}/pause.json"

        resp = requests.get(endpoint, params=self._params)
        self._check_success(resp, f"Failed to pause job {self.id}")

    def resume(self):
        """Resume the Figure Eight job."""
        endpoint = f"{self._base_endpoint}/{self.id}/resume.json"

        resp = requests.get(endpoint, params=self._params)
        self._check_success(resp, f"Failed to resume job {self.id}")

    def cancel(self):
        """Cancel the Figure Eight job."""
        endpoint = f"{self._base_endpoint}/{self.id}/cancel.json"

        resp = requests.get(endpoint, params=self._params)
        self._check_success(resp, f"Failed to cancel job {self.id}")

    def launch(self, on_demand=False, internal=False, n_units=None):
        """Launch the job to your internal and/or the on-demand workforces.

        Args:
            on_demand (bool, optional): Have the on-demand workforce process
                                        `n_units` of rows/units.
            internal (bool, optional): Have the internal workforce process
                                       `n_units` of rows/units.
            n_units (int, optional): The number of rows/units to launch. If
                                     None, all units will be launched.

        """
        if n_units is None:
            status = self.status
            n_units = status["all_units"]
            n_units -= status["golden_units"]
            n_units -= status["ordered_units"]

        n_units = int(n_units)

        if not on_demand and not internal:
            log.warning(
                f"Attempting to launch job {self.id} with no annotators.")

        if not n_units > 0:
            log.warning(
                f"Unable to launch job {self.id} because"
                f" {n_units} units were requested.")

        endpoint = f"{self._base_endpoint}/{self.id}/orders.json"
        n_channels = 0
        data = {"debit[units_count]": n_units}

        if on_demand:
            data.update({f"channels[{n_channels}]": "on_demand"})
            n_channels += 1

        if internal:
            data.update({f"channels[{n_channels}]": "cf_internal"})
            n_channels += 1

        resp = requests.post(endpoint, params=self._params, data=data)
        self._check_success(resp)

    def _get_report(self, report_type):
        endpoint = f"{self._base_endpoint}/{self.id}.csv"
        params = (
            *self._params,
            ("type", report_type)
        )

        resp = requests.get(endpoint, params)
        while resp.status_code == 202:
            sleep(60)
            resp = requests.get(endpoint, params)

        self._check_success(resp)

        csv_zip = ZipFile(BytesIO(resp.content))
        csv_filelike = BytesIO(csv_zip.read(csv_zip.filelist[0].filename))
        csv = pd.read_csv(csv_filelike)
        return csv

    def get_report(self, aggregated=False, full=False):
        """Download the latest Figure Eight report(s) for this job.

        Args:
            aggregated (bool, optional): Download the Figure Eight Aggregated
                                         report for this job.
            full (bool, optional): Download the Figure Eight Full report for
                                   this job.

        Returns:
            pandas.DataFrame, optional: The Aggregated report. Only provided if
                                        `aggregated` is True.
            pandas.DataFrame, optional: The Full report. Only provided if
                                        `full` is True.

        """
        reports = []
        if aggregated:
            reports.append(self._get_report("aggregated"))

        if full:
            reports.append(self._get_report("full"))

        return tuple(reports)


class FigureEightClient(FigureEightAPI):
    """A client for interacting with Figure Eight.

    Currently, it only creates, copies, and deletes jobs.

    """
    def __init__(self, api_key):
        """Initialize a FigureEightClient

        Args:
            api_key (str): Your Figure Eight API key.

        """
        super().__init__(api_key)

    def create_job(self, title, instructions, cml):
        """Create a brand new Figure Eight job.

        Args:
            title (str): The title of this job.
            instructions (str): The instructions html for this job.
            cml (str): The Custom Markup Language task template for this job.

        Returns:
            FigureEightJob: A FigureEightJob object.

        """
        endpoint = f"{self._base_endpoint}.json"

        params = (
            *self._params,
            ("job[title]", title),
            ("job[instructions]", instructions),
            ("job[cml]", cml)
        )
        resp = requests.post(endpoint, params=params)
        self._check_success(resp, "Failed to create new job.")

        job_id = resp.json()["id"]

        return FigureEightJob(self._api_key, job_id)

    def copy_job(self, job_id, units=None):
        """Copy another Figure Eight job.

        Args:
            job_id (str, int): The id of the job to copy from.
            units (str, optional): Which rows/units to copy.
                                   Options: 'all', 'gold', None.
                                   Default: None

        Raises:
            AssertionError: if `units` is not 'all', 'gold', or None

        Returns:
            FigureEightJob: A FigureEightJob object.

        To Do:
            1. Replace `units` with `gold` and `not_gold` booleans
            2. Rename `job_id` to `job` and allow `job` to be a FigureEightJob

        """
        assert(units is None or units == "gold" or units == "all")
        endpoint = f"{self._base_endpoint}/{job_id}/copy.json"

        params = self._params
        if units == "gold":
            params = (*params, ("gold", True))

        if units == "all":
            params = (*params, ("all_units", True))

        resp = requests.get(endpoint, params=params)
        self._check_success(resp)

        return FigureEightJob(self._api_key, resp.json()["id"])

    def delete_job(self, job_id):
        """Delete a Figure Eight Job.

        Args:
            job_id (str, int): The id of the job to delete.

        Returns:
            requests.Response: The response from Figure Eight.

        To Do:
            1. Rename `job_id` to `job` and allow `job` to be a FigureEightJob
            2. Auto-check deletion success. Figure Eight returns 200 codes,
               even on failures.

        """
        endpoint = f"https://api.figure-eight.com/v1/jobs/{job_id}.json"

        resp = requests.delete(endpoint, params=self._params)
        # self._check_success(resp, f"Unable to delete job {job_id}")
        return resp
