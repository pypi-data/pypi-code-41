import json


class DatalakeException(Exception):
    def __init__(self, entity=None, params=None, message=None, response=None):
        if not params and not message:
            message = "%s not found" % entity

        self.params = params
        self.message = (
            message or 'entity with params `{}` not found'.format(params)
        )
        self.entity = entity
        self.response = response

        super(DatalakeException, self).__init__(
            self.message, entity,
            params, message
        )

    def __str__(self):
        return (
            f'\n{self.response.request.method} {self.response.request.url}\n\n'
            f'{json.dumps(self.response.json(), indent=4)}'
        )


class CatalogueEntityNotFoundException(DatalakeException):
    pass


class InvalidPayloadException(DatalakeException):
    pass


class UnAuthorisedAccessException(DatalakeException):
    pass


class InsufficientPrivilegesException(DatalakeException):
    message = 'Insufficient privileges to perform this action'


class S3FileDoesNotExist(DatalakeException):
    def __init__(self, file_path):
        self.message = (
            "Either file at path `%s` does not exist / Potential issue with the bucket policy."
            "Please reach out to Datalake Tech Data Ops user for resolution." % file_path
        )

        super(S3FileDoesNotExist, self).__init__(self.message)


class DownloadFailed(DatalakeException):
    pass


class NoAccountSpecified(DatalakeException):

    def __init__(self, accounts):
        self.accounts = accounts
        self.message = (
            "Unable to default the account for access_manager_id, tech_data_ops_id and/or manager_id "
            "due to multiple accounts being attached to this API key. "
            "Your accounts are: %s" % [(a.id, a.name) for a in accounts]
        )
        super(NoAccountSpecified, self).__init__(self.message)
