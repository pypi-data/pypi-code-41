from cannerflow.request import Request
from cannerflow.saved_query import SavedQuery
from cannerflow.statement import Statement
from cannerflow.file import File

__all__ = ["Workspace"]

class Workspace(object):
    def __init__(
        self,
        endpoint,
        headers,
        workspaceId,
        replaceLocalhostString
    ):
        self.endpoint = endpoint
        self.headers = headers
        self.workspaceId = workspaceId
        request = Request(
            headers=headers,
            endpoint=endpoint
        )
        self.request = request
        self.saved_query = SavedQuery(
            request=request,
            workspaceId=workspaceId
        )
        self.statement = Statement(
            request=request,
            workspaceId=workspaceId
        )
        self.file = File(
            request=request,
            workspaceId=workspaceId,
            replaceLocalhostString=replaceLocalhostString
        )