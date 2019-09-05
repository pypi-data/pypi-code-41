from typing import *

from google.protobuf import wrappers_pb2 as wrappers

from cognite.seismic._api.api import API
from cognite.seismic.data_classes.surface_point_list import SurfacePointList
from cognite.seismic.protos.query_service_messages_pb2 import (
    GeometryTimeSliceQueryRequest,
    LineBasedRectangle,
    LineTimeSliceQueryRequest,
    PositionQuery,
)
from cognite.seismic.protos.types_pb2 import CRS, GeoJson, Geometry, Wkt


class TimeSliceAPI(API):
    def __init__(self, query, metadata):
        super().__init__(query, metadata)

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def get_time_slice_by_lines(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        top_left_inline: int = None,
        top_left_crossline: int = None,
        bottom_right_inline: int = None,
        bottom_right_crossline: int = None,
        z: int = None,
    ):
        file = self.identify(file_id, file_name)
        top_left = PositionQuery(iline=top_left_inline, xline=top_left_crossline)
        bottom_right = PositionQuery(iline=bottom_right_inline, xline=bottom_right_crossline)
        rectangle = LineBasedRectangle(top_left=top_left, bottom_right=bottom_right)
        request = LineTimeSliceQueryRequest(file=file, rectangle=rectangle, z=wrappers.Int32Value(value=z))
        return SurfacePointList([i for i in self.query.GetTimeSliceByLines(request, metadata=self.metadata)])

    def get_time_slice_by_geometry(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        crs: str = None,
        wkt: str = None,
        geo_json=None,
        z: int = None,
    ):
        file = self.identify(file_id, file_name)
        self._verify_input(crs, wkt, geo_json)
        geo = (
            Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))
            if wkt
            else Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json))
        )
        req = GeometryTimeSliceQueryRequest(file=file, geometry=geo, z=wrappers.Int32Value(value=z))
        return SurfacePointList([i for i in self.query.GetTimeSliceByGeometry(req, metadata=self.metadata)])
