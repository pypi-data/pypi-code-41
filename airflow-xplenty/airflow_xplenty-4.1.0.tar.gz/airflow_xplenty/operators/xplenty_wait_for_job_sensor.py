import json
import logging

from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

from airflow_xplenty.client_factory import ClientFactory


class XplentyWaitForJobSensor(BaseSensorOperator):
    """Wait for a job to finish
    """

    SUCCESS_STATUSES = ["completed"]
    FAILED_STATUSES = ["failed", "stopped"]

    @apply_defaults
    def __init__(self, start_job_task_id, **kwargs):
        self.start_job_task_id = start_job_task_id
        self.client = ClientFactory().client()

        super(XplentyWaitForJobSensor, self).__init__(**kwargs)

    def poke(self, context):
        job_id = context["task_instance"].xcom_pull(task_ids=self.start_job_task_id)
        if job_id is None:
            raise Exception("No job_id found in XComs")

        job = self.client.get_job(job_id)
        if job.status in self.FAILED_STATUSES:
            raise Exception("Job failed: %s" % job.errors)
        elif job.status in self.SUCCESS_STATUSES:
            logging.info("Job %d finished in state %s", job_id, job.status)
            logging.info(json.dumps(job.outputs, indent=4))
            context["task_instance"].xcom_push(
                key="xplenty_job_outputs", value=job.outputs
            )
            return True
        else:
            progress = round(job.progress * 100, 1)
            logging.info("Job %d in state %s (%.1f%%)", job_id, job.status, progress)
            return False
