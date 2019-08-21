from cannerflow.cursor import Cursor
__all__ = ["Statement"]

class Statement(object):
    def __init__(
        self,
        workspaceId,
        request
    ):
        self.workspaceId = workspaceId
        self.request = request
    def get_create_payload(self, sql):
        return {
            'operationName': 'createStatement',
            'query': """
                mutation createStatement($data: StatementCreateInput!) {
                    createStatement(data: $data) {
                        id
                        startedAt
                        stats
                        columns
                        data
                        error
                    }
                }
            """,
            'variables': {
                'data': {
                    'sql': sql
                }
            }
        }
    def execute(self, sql=None):
      # if (sql is None):
      #   raise ""
      result = self.request.post(self.get_create_payload(sql)).get('createStatement')
      cursor = Cursor(stats=result['stats'], data=result['data'], columns=result['columns'])
      return cursor