import datetime
import json
from typing import (
    IO,
)

from elasticsearch import Elasticsearch  # type: ignore

from counter_r5.elasticsearch_query import make_search_function
from counter_r5.reports import (
    StandardViewParams,
    make_csv_report,
    get_report_as_sushi_data,
    get_error_response_as_sushi,
    ReportExceptionInfo,
)


class CounterR5Report:
    def __init__(self, report_type: str, customer_id: str, customer_name: str,
                 begin_date: datetime.date,
                 end_date: datetime.date,
                 es_index: str, es_host: str, es_port: int = 9200,
                 with_breakdown_by_month: bool = True,
                 ):
        self.report_type = report_type
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.es_index = es_index
        self.es_host = es_host
        self.es_port = es_port
        self.begin_date = begin_date
        self.end_date = end_date
        self.with_breakdown_by_month = with_breakdown_by_month

    def make_params(self) -> StandardViewParams:
        search_function = make_search_function(self.es_host, self.es_port, self.es_index)
        return StandardViewParams(
            search=search_function, created=datetime.datetime.utcnow(), created_by='Érudit',
            begin_date=self.begin_date, end_date=self.end_date, customer_id=self.customer_id,
            customer_name=self.customer_name, platform='Érudit',
            with_breakdown_by_month=self.with_breakdown_by_month)

    def write_csv(self, f: IO[str]) -> None:
        make_csv_report(self.report_type, f, self.make_params())

    def get_as_sushi_data(self) -> str:
        data = get_report_as_sushi_data(self.report_type, self.make_params())
        return json.dumps(data)

    def get_as_sushi_dict(self) -> dict:
        return get_report_as_sushi_data(self.report_type, self.make_params())

    def get_sushi_error_response(self, error_code: int, severity: str, message: str,
                                 data: str) -> dict:
        report_exception = ReportExceptionInfo(error_code, severity, message, data)
        return get_error_response_as_sushi(self.make_params(), self.report_type, report_exception)
