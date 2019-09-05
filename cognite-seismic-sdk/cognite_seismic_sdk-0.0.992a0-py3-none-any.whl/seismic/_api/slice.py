import google.protobuf.wrappers_pb2 as wrappers
import numpy as np

from cognite.seismic._api.api import API
from cognite.seismic.data_classes.trace_list import Trace2DList
from cognite.seismic.protos.query_service_messages_pb2 import LineSliceQueryRequest
from cognite.seismic.protos.types_pb2 import LineRange, LineSelect


class SliceAPI(API):
    def __init__(self, query, metadata):
        super().__init__(query, metadata)

    @staticmethod
    def _build_range(r_from=None, r_to=None):
        """
        Returns a LineRange based on to and from values
        """
        if r_from or r_to:
            f = wrappers.Int32Value(value=r_from)
            t = wrappers.Int32Value(value=r_to)
            return LineRange(from_line=f, to_line=t)
        else:
            return None

    def _get_slice(self, line_select, file_identifier, include_headers, ort_range):
        request = LineSliceQueryRequest(
            file=file_identifier, line=line_select, include_trace_header=include_headers, range=ort_range
        )
        return Trace2DList([i for i in self.query.GetSliceByLine(request, metadata=self.metadata)])

    def get_inline(self, inline, file_id=None, file_name=None, include_headers=False, from_line=None, to_line=None):
        """
        Returns an inline in a given file. Each trace in the line contains its inline, xline and the values.
        The line can be converted to a 2D numpy array with just the values calling .to_array() on it
        :param inline: inline number (required)
        :param file_id: File can be specified either by name or id (id will be used first if both are provided)
        :param file_name: File can be specified either by name or id (id will be used first if both are provided)
        :param include_headers: Whether or not to include the trace headers in the response
        :param from_line: Include only crosslines equal or greater to this in the slice
        :param to_line: Include only crosslines equal or less than this in the slice
        :return: NP array containing the traces in the requested inline
        """
        return self._get_slice(
            line_select=LineSelect(iline=inline),
            file_identifier=self.identify(file_id, file_name),
            include_headers=include_headers,
            ort_range=self._build_range(from_line, to_line),
        )

    def get_crossline(
        self, crossline, file_id=None, file_name=None, include_headers=False, from_line=None, to_line=None
    ):
        """
        Returns a crossline in a given file. Each trace in the line contains its inline, xline and the values.
        The line can be converted to a 2D numpy array with just the values calling .to_array() on it
        :param crossline: crossline number (required)
        :param file_id: File can be specified either by name or id (id will be used first if both are provided)
        :param file_name: File can be specified either by name or id (id will be used first if both are provided)
        :param include_headers: Whether or not to include the trace headers in the response
        :param from_line: Include only inlines equal or greater to this in the slice
        :param to_line: Include only inlines equal or less than this in the slice
        :return: NP array containing the traces in the requested crossline
        """
        return self._get_slice(
            line_select=LineSelect(xline=crossline),
            file_identifier=self.identify(file_id, file_name),
            include_headers=include_headers,
            ort_range=self._build_range(from_line, to_line),
        )
