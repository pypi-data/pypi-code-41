import logging
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow_xplenty.client_factory import ClientFactory


class XplentyTerminateJobOperator(BaseOperator):
    """Kill a running job
    """

    @apply_defaults
    def __init__(self, start_job_task_id, **kwargs):
        self.start_job_task_id = start_job_task_id
        self.client = ClientFactory().client()

        super(XplentyTerminateJobOperator, self).__init__(**kwargs)

    def execute(self, context):
        job_id = context['task_instance'].xcom_pull(
            task_ids=self.start_job_task_id)
        if job_id is None:
            raise Exception('No job_id found in XComs')

        self.client.stop_job(job_id)
        logging.info('Terminated job %d' % job_id)
