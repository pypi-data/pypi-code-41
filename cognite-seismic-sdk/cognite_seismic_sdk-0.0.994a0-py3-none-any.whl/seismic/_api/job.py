from cognite.seismic._api.api import API
from cognite.seismic.protos.ingest_service_messages_pb2 import StatusRequest


class JobAPI(API):
    def __init__(self, ingestion, metadata):
        super().__init__(metadata=metadata, ingestion=ingestion)

    def status(self, job_id: str = None):
        request = StatusRequest(job_id=job_id)
        return self.ingestion.Status(request=request, metadata=self.metadata)
