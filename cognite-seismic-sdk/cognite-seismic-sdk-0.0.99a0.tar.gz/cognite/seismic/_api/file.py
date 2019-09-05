from typing import *

from cognite.seismic._api.api import API
from cognite.seismic.protos.query_service_messages_pb2 import (
    FileCoverageRequest,
    FileLineQueryRequest,
    FileQueryRequest,
    HeaderFileQueryRequest,
    LineBasedRectangle,
    PositionQuery,
    SegYQueryRequest,
)
from cognite.seismic.protos.types_pb2 import CRS, GeoJson, Geometry, Wkt


class FileAPI(API):
    def __init__(self, query, metadata):
        super().__init__(query, metadata)

    def get_file(self, id: Optional[str] = None, name: Optional[str] = None):
        file = self.identify(id, name)
        request = FileQueryRequest(file=file)
        return self.query.GetFile(request, metadata=self.metadata)

    def get_binary_header(self, id: Optional[str] = None, name: Optional[str] = None, include_raw_header=False):
        file = self.identify(id, name)
        request = HeaderFileQueryRequest(file=file, include_raw_header=include_raw_header)
        return self.query.GetBinaryHeader(request, metadata=self.metadata)

    def get_text_header(self, id: Optional[str] = None, name: Optional[str] = None, include_raw_header=False):
        file = self.identify(id, name)
        request = HeaderFileQueryRequest(file=file, include_raw_header=include_raw_header)
        return self.query.GetTextHeader(request, metadata=self.metadata)

    def get_file_coverage(
        self, id: Optional[str] = None, name: Optional[str] = None, crs: str = "EPSG:23031", in_wkt: bool = False
    ):
        file = self.identify(id, name)
        request = FileCoverageRequest(file=file, crs={"crs": crs}, in_wkt=in_wkt)
        return self.query.GetFileDataCoverage(request, metadata=self.metadata)

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def get_segy_by_lines(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        top_left_inline=None,
        top_left_crossline=None,
        bottom_right_inline=None,
        bottom_right_crossline=None,
    ):
        file = self.identify(file_id, file_name)
        top_left = PositionQuery(iline=top_left_inline, xline=top_left_crossline)
        bottom_right = PositionQuery(iline=bottom_right_inline, xline=bottom_right_crossline)
        rectangle = LineBasedRectangle(top_left=top_left, bottom_right=bottom_right)
        request = SegYQueryRequest(file=file, lines=rectangle)
        return [i for i in self.query.GetSegYFile(request, metadata=self.metadata)]

    def get_segy_by_geometry(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        crs: str = None,
        wkt: str = None,
        geo_json=None,
    ):
        file = self.identify(file_id, file_name)
        self._verify_input(crs, wkt, geo_json)
        geo = (
            Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))
            if wkt
            else Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json))
        )
        request = SegYQueryRequest(file=file, polygon=geo)
        return [i for i in self.query.GetSegYFile(request, metadata=self.metadata)]

    def get_line_range(self, file_id: Optional[str] = None, file_name: Optional[str] = None):
        file = self.identify(file_id, file_name)
        request = FileQueryRequest(file=file)
        return self.query.GetFileLineRange(request, metadata=self.metadata)

    def get_crossline_by_inline(
        self, file_id: Optional[str] = None, file_name: Optional[str] = None, inline: int = None
    ):
        file = self.identify(file_id, file_name)
        request = FileLineQueryRequest(file=file, line=inline)
        return self.query.GetCrosslinesByInline(request, metadata=self.metadata)

    def get_inline_by_crossline(
        self, file_id: Optional[str] = None, file_name: Optional[str] = None, crossline: int = None
    ):
        file = self.identify(file_id, file_name)
        request = FileLineQueryRequest(file=file, line=crossline)
        return self.query.GetInlinesByCrossline(request, metadata=self.metadata)
