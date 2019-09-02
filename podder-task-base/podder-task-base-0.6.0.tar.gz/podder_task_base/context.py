from podder_task_base.databases.pipeline import (
    ReadOnlySession as PipelineReadOnlySession,
    Session as PipelineSession,
)

from .config import Config
from .file import File


class Context(object):
    def __init__(self, dag_id: str) -> None:
        self.config = Config()
        self.file = File()
        self.session = PipelineSession()
        self.read_only_session = PipelineReadOnlySession()
        self.dag_id = dag_id
