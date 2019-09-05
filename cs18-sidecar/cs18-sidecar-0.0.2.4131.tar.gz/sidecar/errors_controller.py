from sidecar.status_maintainer import StatusMaintainer
from sidecar.const import Const
from sidecar.sandbox_error import SandboxError, ErrorCodes
from logging import Logger
from typing import List
import json
from sidecar.utils import Utils


class ErrorsController:
    def __init__(self,  status_maintainer: StatusMaintainer):
        self.status_maintainer = status_maintainer

    def add_sandbox_error(self, error: SandboxError):
        errors = self.status_maintainer.get_sandbox_errors()
        errors.append(error)
        self.status_maintainer.update_sandbox_errors(errors)

    def handle_artifacts_not_found(self, artifacts_not_found):
        if len(artifacts_not_found) > 0:
            error_msg = "Timeout reached while waiting for artifacts.\n" \
                        "Missing artifacts in your artifact storage provider:\n"
            index = 1
            for artifacts_name in artifacts_not_found:
                error_msg += "{INDEX}. {ARTIFACT_NAME}\n".format(INDEX=index, ARTIFACT_NAME=artifacts_name)
                index += 1

            error = SandboxError(Utils.get_utc_now_in_isoformat(), ErrorCodes.ARTIFACTS_DOWNLOAD_FAILED, error_msg)

            self.add_sandbox_error(error)

