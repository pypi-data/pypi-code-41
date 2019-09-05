from typing import *

from cognite.seismic._api.api import API
from cognite.seismic.protos.query_service_messages_pb2 import (
    CoordinateQuery,
    CoordinateTraceQueryRequest,
    LineTraceQueryRequest,
    PositionQuery,
)


class TraceAPI(API):
    def __init__(self, query, metadata):
        super().__init__(query, metadata)

    def get_trace_by_line(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        inline: int = None,
        crossline: int = None,
        include_trace_header: bool = False,
    ):
        file = self.identify(file_id, file_name)
        position = PositionQuery(iline=inline, xline=crossline)
        request = LineTraceQueryRequest(file=file, position=position, include_trace_header=include_trace_header)
        return self.query.GetTraceByLine(request, metadata=self.metadata)

    def get_trace_by_coordinates(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        x: float = None,
        y: float = None,
        max_radius: float = None,
        include_trace_header: bool = False,
    ):
        file = self.identify(file_id, file_name)
        coordinates = CoordinateQuery(x=x, y=y)
        request = CoordinateTraceQueryRequest(
            file=file, coordinates=coordinates, max_radius=max_radius, include_trace_header=include_trace_header
        )
        return self.query.GetTraceByCoordinates(request, metadata=self.metadata)
