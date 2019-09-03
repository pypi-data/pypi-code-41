import copy
import datetime
from collections import OrderedDict
from typing import (
    Callable,
    NamedTuple,
    Optional,
    List,
    Tuple,
    Any,
    Union,
    Iterable,
)

from elasticsearch import Elasticsearch

SearchFunction = Callable[[dict], dict]


class MonthCount(NamedTuple):
    month: datetime.date
    hits: int


class QueryResultData(NamedTuple):
    total_count: int
    top_event: dict
    by_month: Optional[List[MonthCount]]


class QueryResult(NamedTuple):
    total_hits: int
    composite_aggregation_data: List[QueryResultData]
    terms_aggregation_data: dict


def make_search_function(es_host: str, es_port: int, es_index: str) -> SearchFunction:
    client = Elasticsearch([{'host': es_host, 'port': es_port}])

    def search_function(query_body: dict) -> dict:
        return client.search(index=es_index, body=query_body,
                             request_timeout=60)

    return search_function


def get_composite_query_results_data(search: SearchFunction,
                                     query_body: dict) -> QueryResult:
    empty_result_set = False
    all_result_data = []
    after_key = None
    terms_aggregation_data = None
    total_hits = None
    while not empty_result_set:
        if after_key:
            query_body = copy.deepcopy(query_body)
            query_body['aggs']['composite_agg']['composite']['after'] = after_key
        result = search(query_body)
        after_key, result_data = extract_result_data_from_composite_elasticsearch_result(result)
        if terms_aggregation_data is None:
            terms_aggregation_data = {
                agg_name: agg_data for agg_name, agg_data in result['aggregations'].items()
                if agg_name != 'composite_agg'
            }
            total_hits = result['hits']['total']
        all_result_data.extend(result_data)
        empty_result_set = after_key is None

    return QueryResult(
        total_hits=total_hits,
        composite_aggregation_data=all_result_data,
        terms_aggregation_data=terms_aggregation_data
    )


def extract_result_data_from_composite_elasticsearch_result(
        query_result: dict) -> Tuple[dict, List[QueryResultData]]:
    aggregations = query_result['aggregations']['composite_agg']
    buckets = aggregations['buckets']
    # if buckets are empty (ie. no more data), after_key is absent
    after_key = aggregations.get('after_key', None)
    return after_key, [extract_result_data(bucket) for bucket in buckets]


def extract_result_data(bucket: dict) -> QueryResultData:
    by_month = []
    if 'hits_over_months' in bucket:
        hits_over_months = bucket['hits_over_months']['buckets']
        for month_bucket in hits_over_months:
            month_as_date = parse_r5_date(month_bucket['key_as_string'])
            hits_by_month = MonthCount(
                month=month_as_date.date(),
                hits=month_bucket['doc_count']
            )
            by_month.append(hits_by_month)

    return QueryResultData(
        total_count=bucket['doc_count'],
        top_event=bucket['event_top_hit']['hits']['hits'][0]['_source'],
        by_month=by_month or None
    )


def parse_r5_date(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, '%Y-%m-%d')


def get_last_aggs(with_breakdown_by_month: bool) -> dict:
    aggs = {
        "event_top_hit": {
            "top_hits": {
                "sort": [
                    {
                        "timestamp": {
                            "order": "desc"
                        }
                    }
                ],
                "size": 1
            }
        },
    }
    if with_breakdown_by_month:
        aggs["hits_over_months"] = {
            "date_histogram": {
                "field": "timestamp",
                "interval": "month",
                "format": "yyyy-MM-dd"
            }
        }
    return aggs


class AggregatedField(NamedTuple):
    name: str
    include_missing_bucket: bool

    def get_source_dict(self):
        terms = {"field": self.name}
        if self.include_missing_bucket:
            terms["missing_bucket"] = self.include_missing_bucket
        return {self.name: {"terms": terms}}


AggregationInfo = Union[AggregatedField, str]


def make_composite_aggregation(fields: Iterable[AggregationInfo],
                               with_breakdown_by_month: bool) -> dict:
    sources = []
    for field in fields:
        if isinstance(field, str):
            field = AggregatedField(field, False)
        sources.append(field.get_source_dict())
    aggs = {
        "aggs": {
            "composite_agg": {
                "composite": {
                    "size": 1000,
                    "sources": sources
                },
                "aggregations": get_last_aggs(with_breakdown_by_month)
            }
        }
    }
    return aggs


def build_usage_query(begin_date: datetime.date, end_date: datetime.date,
                      must_terms: Iterable[Tuple[str, Any]],
                      composite_aggregation_fields: Iterable[AggregationInfo],
                      terms_aggregation_fields: Iterable[str],
                      with_breakdown_by_month: bool) -> dict:
    query_body = make_composite_aggregation(composite_aggregation_fields, with_breakdown_by_month)
    for field in terms_aggregation_fields:
        query_body['aggs'][field] = {'terms': {'field': field, 'size': 1000}}
    query_body['size'] = 0
    query_body['query'] = {'bool': {'must': []}}
    must_clauses = query_body['query']['bool']['must']
    must_clauses.append(date_range(begin_date, end_date))
    must_clauses.extend([
        {'term': {"is_double_click": False}},
    ])
    if must_terms:
        for term in must_terms:
            must_clauses.append({'term': {term[0]: term[1]}})

    return query_body


def date_range(begin_date: datetime.date, end_date: datetime.date) -> dict:
    return {'range': {'timestamp': {'gte': format_date(begin_date),
                                    'lt': format_date(end_date),
                                    'format': 'yyyy-MM-dd'}}}


def format_date(d: datetime.date):
    return d.strftime('%Y-%m-%d')


def extract_stats_by_month(by_month: Optional[List[MonthCount]]) -> 'OrderedDict[str, int]':
    if not by_month:
        return OrderedDict()
    stats_by_month: 'OrderedDict[str, int]' = OrderedDict()
    for month_count in by_month:
        first_day_of_month = month_count.month
        month_str = month_as_str(first_day_of_month)
        stats_by_month[month_str] = month_count.hits
    return stats_by_month


def month_as_str(first_day_of_month):
    month_number = first_day_of_month.month
    year = first_day_of_month.year
    month_str = f'{MONTHS[month_number - 1]}-{year}'
    return month_str


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
