from typing import Any, List

from podder_task_base import Context
from podder_task_base.log import logger

DATA_PATH = "data/"


@logger.class_logger
class BaseTask(object):
    """
    Abstract task class.
    Please add your concrete code to concrete task class: `app/task.py`.
    """

    def __init__(self, context: Context) -> None:
        self.context = context
        self.set_arguments()
        self.logger.init_tasktime()

    def execute(self, inputs: List[Any]) -> List[Any]:
        pass

    def set_arguments(self) -> None:
        pass
