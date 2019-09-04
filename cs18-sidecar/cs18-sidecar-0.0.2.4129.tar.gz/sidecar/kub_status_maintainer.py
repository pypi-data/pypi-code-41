from sidecar.const import Const
from sidecar.utils import Utils
from sidecar.status_maintainer import StatusMaintainer
from sidecar.kub_api_service import IKubApiService
from sidecar.sandbox_error import SandboxError
from logging import Logger
from typing import List
import json


class KUBStatusMaintainer(StatusMaintainer):
    def __init__(self, logger: Logger, kub_api_service: IKubApiService):
        super().__init__(logger)
        self.kub_api_service = kub_api_service

    # annotation is like an item in a dynamoDB
    def update_annotation_in_namespace(self, key: str, value: str):
        annotation = {key: value}
        self.kub_api_service.update_namespace(annotation)

    def update_lazy_load_artifacts_waiting(self, value: bool):
        self.update_annotation_in_namespace(Const.LAZY_LOAD_ARTIFACTS_WAITING, str(value))

    def update_sandbox_errors(self, errors: List[SandboxError]):
        errors_to_db = [{"message": error.message, "code": error.code, "time": error.time} for error in errors]
        self.update_annotation_in_namespace(Const.SANDBOX_ERRORS, json.dumps(errors_to_db))

    def update_qualiy_status(self, status: str):
        self.update_annotation_in_namespace(Const.QUALIY_STATUS, status)

    def get_sandbox_errors(self) -> List[SandboxError]:
        try:
            errors_in_jason_format = self.kub_api_service.get_json_annotation(Const.SANDBOX_ERRORS)
            if errors_in_jason_format is None:
                return []

            errors = []
            for error in errors_in_jason_format:
                errors.append(SandboxError(message=str(error["message"]),
                                           code=str(error["code"]),
                                           time=str(error["time"])))
            return errors

        except Exception as e:
            return []

