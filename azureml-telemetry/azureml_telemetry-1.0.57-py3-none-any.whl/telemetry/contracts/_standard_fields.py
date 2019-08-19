# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Standard fields in the logging schema. a.k.a Part B."""
from typing import Any, List


class StandardFieldKeys:
    """Keys for standard fields."""

    ALGORITHM_TYPE_KEY = 'AlgorithmType'
    CLIENT_OS_KEY = 'ClientOS'
    COMPUTE_TYPE_KEY = 'ComputeType'
    HTTP_METHOD = "HttpMethod"
    HTTP_STATUS_CODE = "HttpStatusCode"
    HTTP_USER_AGENT = "HttpUserAgent"
    ITERATION_ID_KEY = 'IterationId'
    JOB_STATUS_KEY = 'JobStatus'
    PARENT_RUN_ID_KEY = 'ParentRunId'
    RESOURCE_GROUP_KEY = 'ResourceGroup'
    RUN_ID_KEY = 'RunId'
    SUB_COMPONENT_TYPE_KEY = 'SubComponentType'
    TASK_TYPE_KEY = 'TaskType'
    WORKSPACE_REGION_KEY = 'WorkspaceRegion'

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for standard fields."""
        return [
            StandardFieldKeys.ALGORITHM_TYPE_KEY,
            StandardFieldKeys.CLIENT_OS_KEY,
            StandardFieldKeys.COMPUTE_TYPE_KEY,
            StandardFieldKeys.HTTP_METHOD,
            StandardFieldKeys.HTTP_STATUS_CODE,
            StandardFieldKeys.HTTP_USER_AGENT,
            StandardFieldKeys.ITERATION_ID_KEY,
            StandardFieldKeys.JOB_STATUS_KEY,
            StandardFieldKeys.PARENT_RUN_ID_KEY,
            StandardFieldKeys.RESOURCE_GROUP_KEY,
            StandardFieldKeys.RUN_ID_KEY,
            StandardFieldKeys.SUB_COMPONENT_TYPE_KEY,
            StandardFieldKeys.TASK_TYPE_KEY,
            StandardFieldKeys.WORKSPACE_REGION_KEY
        ]


class StandardFields(dict):
    """Standard fields in the logging schema. a.k.a Part B."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize a new instance of the StandardFields."""
        super(StandardFields, self).__init__(*args, **kwargs)

    @property
    def algorithm_type(self):
        """Component Name."""
        return self.get(StandardFieldKeys.ALGORITHM_TYPE_KEY, None)

    @algorithm_type.setter
    def algorithm_type(self, value):
        """
        Set Component Name.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.ALGORITHM_TYPE_KEY] = value

    @property
    def client_os(self):
        """Get the client operating system."""
        return self.get(StandardFieldKeys.CLIENT_OS_KEY, None)

    @client_os.setter
    def client_os(self, value):
        """
        Set the client operating system.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.CLIENT_OS_KEY] = value

    @property
    def compute_type(self):
        """Compute Type."""
        return self.get(StandardFieldKeys.COMPUTE_TYPE_KEY, None)

    @compute_type.setter
    def compute_type(self, value):
        """
        Set Compute Type.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.COMPUTE_TYPE_KEY] = value

    @property
    def http_method(self):
        """Http method used."""
        return self.get(StandardFieldKeys.HTTP_METHOD, None)

    @http_method.setter
    def http_method(self, value):
        """
        Set http method used.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.HTTP_METHOD] = value

    @property
    def http_status_code(self):
        """Http status code returned."""
        return self.get(StandardFieldKeys.HTTP_STATUS_CODE, None)

    @http_status_code.setter
    def http_status_code(self, value):
        """
        Set http status code returned.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.HTTP_STATUS_CODE] = value

    @property
    def http_user_agent(self):
        """Http user agent."""
        return self.get(StandardFieldKeys.HTTP_USER_AGENT, None)

    @http_user_agent.setter
    def http_user_agent(self, value):
        """
        Set http user agent.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.HTTP_USER_AGENT] = value

    @property
    def iteration_id(self):
        """Id for iteration."""
        return self.get(StandardFieldKeys.ITERATION_ID_KEY, None)

    @iteration_id.setter
    def iteration_id(self, value):
        """
        Set Iteration Id.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.ITERATION_ID_KEY] = value

    @property
    def job_status(self):
        """Job status."""
        return self.get(StandardFieldKeys.JOB_STATUS_KEY, None)

    @job_status.setter
    def job_status(self, value):
        """
        Set job status.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.JOB_STATUS_KEY] = value

    @property
    def parent_run_id(self):
        """Parent run id."""
        return self.get(StandardFieldKeys.PARENT_RUN_ID_KEY, None)

    @parent_run_id.setter
    def parent_run_id(self, value):
        """
        Set parent run id.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.PARENT_RUN_ID_KEY] = value

    @property
    def resource_group(self):
        """Get the client operating system."""
        return self.get(StandardFieldKeys.RESOURCE_GROUP_KEY, None)

    @resource_group.setter
    def resource_group(self, value):
        """
        Set the client operating system.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.RESOURCE_GROUP_KEY] = value

    @property
    def run_id(self):
        """Run id."""
        return self.get(StandardFieldKeys.RUN_ID_KEY, None)

    @run_id.setter
    def run_id(self, value):
        """
        Set Rund Id.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.RUN_ID_KEY] = value

    @property
    def sub_component_type(self):
        """Component Name."""
        return self.get(StandardFieldKeys.SUB_COMPONENT_TYPE_KEY, None)

    @sub_component_type.setter
    def sub_component_type(self, value):
        """
        Set Component Name.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.SUB_COMPONENT_TYPE_KEY] = value

    @property
    def task_type(self):
        """Workspace region."""
        return self.get(StandardFieldKeys.TASK_TYPE_KEY, None)

    @task_type.setter
    def task_type(self, value):
        """
        Workspace region to set to.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.TASK_TYPE_KEY] = value

    @property
    def workspace_region(self):
        """Workspace region."""
        return self.get(StandardFieldKeys.WORKSPACE_REGION_KEY, None)

    @workspace_region.setter
    def workspace_region(self, value):
        """
        Workspace region to set to.

        :param value: Value to set to.
        """
        self[StandardFieldKeys.WORKSPACE_REGION_KEY] = value
