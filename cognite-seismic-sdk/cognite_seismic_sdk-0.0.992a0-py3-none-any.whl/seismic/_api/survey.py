from typing import *

from cognite.seismic._api.api import API
from cognite.seismic.protos.query_service_messages_pb2 import (
    ListSurveysQueryRequest,
    MetadataFilter,
    SearchSurveyRequest,
    SurveyQueryRequest,
)
from cognite.seismic.protos.types_pb2 import CRS, GeoJson, Geometry, Wkt


class SurveyAPI(API):
    def __init__(self, query, metadata):
        super().__init__(query, metadata)

    def get(self, id: Optional[str] = None, name: Optional[str] = None, list_files=True, include_metadata=False):
        survey = self.identify(id, name)
        req = SurveyQueryRequest(survey=survey, list_files=list_files, include_metadata=include_metadata)
        return self.query.GetSurvey(req, metadata=self.metadata)

    def list(self):
        return self.query.ListSurveys(ListSurveysQueryRequest(), metadata=self.metadata)

    @staticmethod
    def _verify_input(wkt: str = None, geo_json: str = None):
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def search(
        self,
        crs: str,
        wkt: str = None,
        geo_json=None,
        survey_metadata_filter: dict = None,
        file_metadata_filter: dict = None,
        include_metadata: bool = False,
    ):
        geo = (
            Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))
            if wkt
            else Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json))
        )
        if survey_metadata_filter and file_metadata_filter:
            request = SearchSurveyRequest(
                polygon=geo,
                survey_metadata=MetadataFilter(filter=survey_metadata_filter),
                file_metadata=MetadataFilter(filter=file_metadata_filter),
                include_metadata=include_metadata,
            )
        elif survey_metadata_filter and not file_metadata_filter:
            request = SearchSurveyRequest(
                polygon=geo,
                survey_metadata=MetadataFilter(filter=survey_metadata_filter),
                include_metadata=include_metadata,
            )
        elif not survey_metadata_filter and file_metadata_filter:
            request = SearchSurveyRequest(
                polygon=geo,
                file_metadata=MetadataFilter(filter=file_metadata_filter),
                include_metadata=include_metadata,
            )
        else:
            request = SearchSurveyRequest(polygon=geo, include_metadata=include_metadata)
        return self.query.SearchSurveys(request, metadata=self.metadata)
