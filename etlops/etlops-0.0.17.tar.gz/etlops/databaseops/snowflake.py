import logging
from etlops.clients.mpp import SnowflakeClient
from etlops.databaseops.abstracts import QuerySequence
from retrying import retry

class SnowflakeQuerySequence(QuerySequence):

    QUERY_CONTEXT_FIELD = "QueryContext"
    WAREHOUSE_FIELD = "Warehouse"

    def __init__(self, queries: dict, client: SnowflakeClient, metadata: dict):
        self.queries = queries
        self.client = client
        self.metadata = metadata
        self.parse_execution_order()
        self.logger = logging.getLogger('SnowflakeQuerySequence')

    def execute(self) -> None:
        self.client.connect()
        try:
            for query_index in self.query_execution_order:
                self.run_query(query_index=query_index)
        finally:
            self.client.disconnect()

    @retry(stop_max_attempt_number=3, wait_random_min=1000, wait_random_max=5000)
    def run_query(self, query_index: str) -> None:
        self.logger.info('Running query index: {query_index}'.format(query_index=str(query_index)))
        self.setup_query_context(query_context=self.metadata[str(query_index)][self.QUERY_CONTEXT_FIELD])
        self.client.dml_query(query_string=self.queries[str(query_index)])

    def setup_query_context(self, query_context: dict) -> None:
        for parameter, value in query_context.items():
            self.client.switch_to(parameter, value)
            if parameter == self.WAREHOUSE_FIELD:
                self.client.alter_warehouse(value, self.client.RESUME_COMMAND)
