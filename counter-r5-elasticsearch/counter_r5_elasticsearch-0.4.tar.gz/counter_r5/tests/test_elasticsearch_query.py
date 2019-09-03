import datetime
import json
from pathlib import Path

from counter_r5.elasticsearch_query import (
    extract_result_data,
    QueryResultData,
    MonthCount,
    extract_result_data_from_composite_elasticsearch_result,
    AggregatedField,
    extract_stats_by_month,
    get_composite_query_results_data,
)

TEST_BUCKET = {
    "key": "1044608ar",
    "doc_count": 3,
    "event_top_hit": {
        "hits": {"hits": [{"_source": {'expected': 1}, }]}
    },
    "hits_over_months": {
        "buckets": [
            {"key_as_string": "2018-01-01", "key": 1514764800000, "doc_count": 1},
            {"key_as_string": "2018-01-02", "key": 1517443200000, "doc_count": 2},
        ]
    }
}


def test_extract_result_data():
    extracted = extract_result_data(TEST_BUCKET)
    assert extracted == QueryResultData(3, {'expected': 1},
                                        by_month=[MonthCount(datetime.date(2018, 1, 1), 1),
                                                  MonthCount(datetime.date(2018, 1, 2), 2), ])


def test_extract_result_data_without_hits_per_months():
    test_bucket_without_months = TEST_BUCKET.copy()
    del test_bucket_without_months['hits_over_months']
    extracted = extract_result_data(test_bucket_without_months)
    assert extracted == QueryResultData(3, {'expected': 1}, by_month=None)


def test_extract_result_data_from_elasticsearch_result():
    result = get_elasticsearch_fixture('tr_j1_result.json')
    _, extracted = extract_result_data_from_composite_elasticsearch_result(result)
    assert len(extracted) == 2
    assert set(e.top_event['is_unique'] for e in extracted) == {0, 1}
    expected_by_month = [MonthCount(datetime.date(2018, m, 1), 1) for m in range(1, 13)]
    assert extracted[0].by_month == expected_by_month


def get_elasticsearch_fixture(filename):
    with open(Path(__file__).parent / filename) as f:
        result = json.load(f)
    return result


class TestAggregatedField:
    def test_can_exclude_missing(self):
        assert AggregatedField('abc', False).get_source_dict() == {
            'abc': {'terms': {'field': 'abc'}}
        }

    def test_can_include_missing(self):
        assert AggregatedField('abc', True).get_source_dict() == {
            'abc': {'terms': {'field': 'abc', 'missing_bucket': True}}
        }


def test_extract_stats_by_month():
    by_month = [MonthCount(datetime.date(2018, m, 1), 1) for m in range(1, 13)]
    months_dict = list(extract_stats_by_month(by_month).items())
    assert months_dict == [('Jan-2018', 1), ('Feb-2018', 1), ('Mar-2018', 1),
                           ('Apr-2018', 1), ('May-2018', 1), ('Jun-2018', 1),
                           ('Jul-2018', 1), ('Aug-2018', 1), ('Sep-2018', 1),
                           ('Oct-2018', 1), ('Nov-2018', 1), ('Dec-2018', 1), ]


def test_extract_non_composite_aggregations():
    # noinspection PyUnusedLocal
    def search(q: dict) -> dict:
        return {
            'aggregations': {
                'composite_agg': {
                    'buckets': []
                },
                'unique_ids': {
                    'buckets': {}
                }
            },
            'hits': {
                'total': 12,
            }
        }

    result = get_composite_query_results_data(search, {})
    assert result.total_hits == 12
    assert list(result.terms_aggregation_data.keys()) == ['unique_ids']
