from etlops.clients.rdbms import MySQLClient
from etlops.databaseops.abstracts import QuerySequence


class MySQLTransaction(QuerySequence):

    QUERY_CONTEXT_FIELD = "QueryContext"
    START_TRANSACTION_QUERY = 'START TRANSACTION;'
    COMMIT_QUERY = 'COMMIT;'

    def __init__(self, queries: dict, client: MySQLClient, metadata: dict):
        self.queries = queries
        self.client = client
        self.metadata = metadata
        self.parse_execution_order()

    def execute(self) -> None:
        self.client.connect()
        try:
            self.client.dml_query(query_string=MySQLTransaction.START_TRANSACTION_QUERY)
            for query_index in self.query_execution_order:
                self.run_query(query_index=query_index)
            self.client.dml_query(query_string=MySQLTransaction.COMMIT_QUERY)
        finally:
            self.client.disconnect()

    def run_query(self, query_index: str) -> None:
        self.setup_query_context(query_context=self.metadata[str(query_index)][self.QUERY_CONTEXT_FIELD])
        self.client.dml_query(query_string=self.queries[str(query_index)])

    def setup_query_context(self, query_context: dict) -> None:
        for parameter, value in query_context.items():
            self.client.switch_to(value)
