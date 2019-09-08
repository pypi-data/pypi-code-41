class SandboxError:
    def __init__(self, time: str, code: str, message: str):
        self.message = message
        self.code = code
        self.time = time


class ErrorCodes:
    ARTIFACTS_DOWNLOAD_FAILED = "ARTIFACTS_DOWNLOAD_FAILED"
    ENDING_FAILED = "ENDING_FAILED"

