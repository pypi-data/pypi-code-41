import os

import grpc

import cognite.seismic.protocompiled.query_service_pb2_grpc as qserv
from cognite.seismic._api.file import FileAPI
from cognite.seismic._api.survey import SurveyAPI
from cognite.seismic._api.time_slice import TimeSliceAPI
from cognite.seismic._api.trace import TraceAPI
from cognite.seismic._api.volume import VolumeAPI


class CogniteSeismicClient:
    """
    Main class for the seismic client
    """

    def __init__(self, api_key=None, base_url=None, port=None):
        # configure env

        self.api_key = api_key or os.getenv("COGNITE_API_KEY")
        self.base_url = base_url or "api-grpc.cognitedata.com"
        self.port = port or "443"
        self.url = self.base_url + ":" + self.port
        self.metadata = [("api-key", self.api_key)]

        # start the connection

        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(
            self.url, credentials, options=[("grpc.max_receive_message_length", 10 * 1024 * 1024)]
        )
        self.query = qserv.QueryStub(channel)

        self.survey = SurveyAPI(self.query, self.metadata)
        self.trace = TraceAPI(self.query, self.metadata)
        self.file = FileAPI(self.query, self.metadata)
        self.volume = VolumeAPI(self.query, self.metadata)
        self.time_slice = TimeSliceAPI(self.query, self.metadata)
