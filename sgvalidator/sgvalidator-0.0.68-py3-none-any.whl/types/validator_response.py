from .validator_status import ValidatorStatus


class ValidatorResponse:
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

        assert(status == ValidatorStatus.FAIL or status == ValidatorStatus.SUCCESS or
               status == ValidatorStatus.WARN or status == ValidatorStatus.IGNORED)

        if status == ValidatorStatus.FAIL:
            assert(message is not None)

    def getStatus(self):
        return self.status

    def getMessage(self):
        return self.message
