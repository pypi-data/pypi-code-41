"""
Primary Interface with webservice. `oaas_sdk.sdk.LabelingTask` as well as the reference methods can be imported directly from the module, as:
`from oaas_sdk import LabelingTask, get_companies, get_labeling_solutions`.
"""

import time
from typing import Union, Optional, Iterable, Set

import pandas as pd

from oaas_sdk.objects import ResultNotReady, FailedLabelingTask, PurgedLabelingTask
from oaas_sdk.util import UPDATE_FREQUENCY
from oaas_sdk.ws import client


class LabelingTask:
    """
    Object representation of a labeling task. Can be used to check status and retrieve results. Fields on this object will automatically retrieve/update
    information from webservice.
    """
    labeling_solutions = None

    def __init__(self, task_id: str):
        """Initializes an existing or recently created labeling task."""

        self.task_id = task_id
        """Webservice assigned ID of labeling task"""

        self._last_status_update = 0
        self._status = None
        self._result = None

    @classmethod
    def create(cls, data: pd.DataFrame, labeling_solution_category: str = 'verified',
               labeling_solution_name: str = 'label', *,
               companies: Optional[Iterable[str]] = None, output_format: str = 'arrow'):
        """
        Submits a new labeling task to be processed in the webservice. Input data is expected to be in the form of a DataFrame with these columns:

        - `document_id` _(optional)_: If present, will be passed through as a used provided ID. The input data's order is preserved during processing so this is entirely
          optional.
        - `product_description` _(required)_: Primary product description for this datum.
        - `from_email` _(optional)_: A domain or email address which is the source of this product description, if known.

        Args:
            labeling_solution_category: A category of labeling solution to apply to this data. Available categories can be found with _*TODO NEED A LINK WHEN ADDED*_
            labeling_solution_name: A labeling solution name to apply to this data. Available names can be found with _*TODO NEED A LINK WHEN ADDED*_
            data: A pandas DataFrame with the columns specified above.
            companies: If desired, search space can be restricted by specifying a list of companies here. Available companies can be found with _*TODO NEED A LINK WHEN ADDED*_
            output_format: By default, output will be retrieved through this SDK as a pandas DataFrame. If you wish to have results in another format (such as
                           json or csv) specify so here.

        Returns:
            A `oaas_sdk.sdk.LabelingTask` object which can be used to check status and retrieve results when finished processing.
        """
        task_id = client.create_new_labeling_task(labeling_solution_category, labeling_solution_name, data,
                                                  companies=companies,
                                                  output_format=output_format)
        return cls(task_id)

    @property
    def status(self) -> str:
        """
        Current status of labeling task.
        Returns:
            One of: [submitted, processed, failed, skipped, purged]
        """
        # update with webservice if it's been long enough
        if time.time() - self._last_status_update > UPDATE_FREQUENCY:
            self._status = client.get_labeling_task_status(self.task_id)
            self._last_status_update = time.time()

        return self._status

    @property
    def result(self) -> Union[pd.DataFrame, str]:
        """
        Retrieve result, as a DataFrame or string of json/csv depending on selected output_format, from webservice. Caches value so multiple calls
        won't requery the webservice.
        Raises:
            `oaas_sdk.objects.ResultNotReady`
            `oaas_sdk.objects.FailedLabelingTask`
            `oaas_sdk.objects.PurgedLabelingTask`
        """
        # If we've retrieved the result before, don't requery.
        if self._result is not None:
            return self._result

        # If not, check on the status of the job.
        status = self.status

        if status == 'submitted':
            raise ResultNotReady
        elif status == 'failed':
            raise FailedLabelingTask
        elif status == 'purged':
            raise PurgedLabelingTask
        else:
            self._result = client.get_labeling_task_content(self.task_id)
            return self._result

    def join(self, timeout: int = 0) -> Union[pd.DataFrame, str, None]:
        """
        Blocks while waiting for labeling task to complete, and returns result.
        Args:
            timeout: If labeling task is still processing after this many seconds, raise a `TimeoutError`. 0 means to wait indefinitely.
        Returns:
            Result of labeling task. Typically a DataFrame, but could be a string representing json or csv if that output_format was specified when labeling task was created.

        Raises:
            `TimeoutError`

        """
        if timeout:
            end_time = time.time() + timeout
        else:
            end_time = None
        while True:
            if end_time:
                if time.time() > end_time:
                    raise TimeoutError

            try:
                return self.result
            except ResultNotReady:
                pass

            # sleep so we don't use an entire core just spinning through this loop
            time.sleep(UPDATE_FREQUENCY)


# Other reference methods
def get_companies(labeling_solution_category: str, labeling_solution_name: str) -> Set[str]:
    """
    Get all possible companies supported by the given labeling solution. Members of this set can be used when submitting a labeling job to limit the search
    space. Also, any matches from this labeling solution are guaranteed to be a member of this set, or one of the special match types (other, generic, etc.)
    Args:
         labeling_solution_category: A category of labeling solution to apply to this data. Available categories can be found with
                                     `oaas_sdk.sdk.get_labeling_solutions`
         labeling_solution_name: A labeling solution name to apply to this data. Available names can be found with `oaas_sdk.sdk.get_labeling_solutions`
    Returns:
        List of possible company values for the specified labeling_solution_category and labeling_solution name.
     """
    return client.get_company_set(labeling_solution_category, labeling_solution_name)


def get_labeling_solutions():
    """
    Get all possible labeling solutions supported by your version of OaaS.
    Returns:
        Dictionary of available labeling "solutions". The category/name pairs are the possible arguments to the `LabelingTask.submit` method, as well as the
            `oaas_sdk.sdk.get_companies` method.
    """
    return client.get_labeling_solutions()
