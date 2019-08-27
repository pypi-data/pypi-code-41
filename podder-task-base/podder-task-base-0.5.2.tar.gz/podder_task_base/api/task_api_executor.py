import json
import traceback
from pathlib import Path
from typing import Tuple, Iterator, Any

from podder_task_base import Context, settings
from podder_task_base.log import logger


@logger.class_logger
class TaskApiExecutor(object):
    def __init__(self, execution_task, gprc_pb2):
        self.execution_task = execution_task
        self.gprc_pb2 = gprc_pb2

    def execute(self, request: Any, _context: Any):
        settings.init()
        dag_id = request.dag_id
        context = Context(dag_id)

        try:
            inputs, job_id, task_name = self._parse_request_and_load_arg_file(request)
            outputs = self.execution_task(context).execute(inputs)
            task_response = self._generate_arg_file_and_convert_to_task_response(
                dag_id, job_id, task_name, outputs)

        except Exception:
            self.logger.error(traceback.format_exc())
            return self._make_error_task_response(dag_id)

        return task_response

    @staticmethod
    def _parse_request_and_load_arg_file(request: Any) -> Tuple[list, str, str]:
        inputs = []
        job_id = ""
        task_name = ""
        for result in request.results:
            job_id = result.job_id
            job_data = json.loads(result.job_data)
            task_name = job_data['task_name']

            arg_file = Path(job_data['arg_file'])
            with arg_file.open() as file:
                arg_data = json.loads(file.read())

            inputs.append({'job_id': job_id, 'job_data': arg_data})
        return inputs, job_id, task_name

    def _generate_arg_file_and_convert_to_task_response(self, dag_id: str, job_id: str,
                                                        task_name: str, outputs: Iterator[Any]):
        task_response = self.gprc_pb2.TaskResponse()
        task_response.dag_id = dag_id
        for i, output in enumerate(outputs):
            arg_file = Path('/usr/local/poc_base/tmp/{}/{}/arg/{}_{}.json'.format(
                dag_id, job_id, task_name, i))
            with arg_file.open('w') as file:
                file.write(json.dumps(output['job_data']))

            task_response.results.add(
                job_id=output['job_id'], job_data=json.dumps({
                    'arg_file': str(arg_file)
                }))
        return task_response

    def _make_error_task_response(self, dag_id: str):
        task_response = self.gprc_pb2.TaskResponse()
        task_response.dag_id = dag_id
        return task_response
