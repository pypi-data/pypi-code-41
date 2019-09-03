import datetime

from counter_r5.reports import (
    get_tr_j1_query,
    get_ir_a1_query,
    get_tr_j3_query,
    get_tr_j1_data,
)
from .build_fixtures import make_params


class TestJournalRequestsControlledAccess:
    """Tests for TR_J1 report. """
    def test_one_controlled_access_each_month(self, one_controlled_access_for_one_item_every_month):
        client = one_controlled_access_for_one_item_every_month
        query_body = get_tr_j1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 12

    def test_aggregations(self, one_controlled_access_for_one_item_every_month):
        client = one_controlled_access_for_one_item_every_month
        query_body = get_tr_j1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        buckets = res['aggregations']['composite_agg']['buckets']
        assert len(buckets) == 1
        assert buckets[0]['key'] == {'parent_proprietary_id': 'bo',
                                     'is_unique': True}
        top_event_source = buckets[0]['event_top_hit']['hits']['hits'][0]['_source']
        assert top_event_source['parent_proprietary_id'] == 'bo'

    def test_more_than_thousand(self, two_thousand_accesses):
        client = two_thousand_accesses

        def search(query: dict) -> dict:
            return client.search(index="tests_counter_r5", body=query)

        params = make_params(datetime.date(2018, 1, 1), datetime.date(2019, 1, 1),
                             search_fn=search)
        results = get_tr_j1_data(params)
        assert len(results.results_data) == 2000

    def test_filter_institution(self, one_access_for_one_item_every_month_two_institutions):
        client = one_access_for_one_item_every_month_two_institutions
        query_body = get_tr_j1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 12

    def test_one_controlled_access_each_month_first_6_months(
            self, one_controlled_access_for_one_item_every_month):
        client = one_controlled_access_for_one_item_every_month
        query_body = get_tr_j1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2018, 7, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 6

    def test_alternate_controlled_and_oa_access_each_month(
            self, alternate_controlled_and_oa_for_one_item_every_month):
        client = alternate_controlled_and_oa_for_one_item_every_month
        query_body = get_tr_j1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 12

    def test_dont_filter_based_on_unique_or_not(
            self, alternate_unique_and_not_for_one_item_every_month):
        client = alternate_unique_and_not_for_one_item_every_month
        query_body = get_tr_j1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 24


class TestItemRequestsArticle:
    """Tests for IR_A1 report. """
    def test_one_controlled_access_each_month(self, one_controlled_access_for_one_item_every_month):
        client = one_controlled_access_for_one_item_every_month
        query_body = get_ir_a1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 12

    def test_alternate_controlled_and_oa_access_each_month(
            self, alternate_controlled_and_oa_for_one_item_every_month):
        client = alternate_controlled_and_oa_for_one_item_every_month
        query_body = get_ir_a1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 24

    def test_aggregations(self, alternate_controlled_and_oa_for_one_item_every_month):
        client = alternate_controlled_and_oa_for_one_item_every_month
        query_body = get_ir_a1_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        buckets = res['aggregations']['composite_agg']['buckets']
        assert len(buckets) == 2
        assert buckets[0]['key'] == {'proprietary_id': '1044608ar',
                                     'is_unique': True, 'access_type': 'Controlled'}
        top_event_source = buckets[0]['event_top_hit']['hits']['hits'][0]['_source']
        assert top_event_source['proprietary_id'] == '1044608ar'


class TestJournalRequestsByAccessType:
    """Tests for TR_J3 report. """
    def test_alternate_controlled_and_oa_access_each_month(
            self, alternate_controlled_and_oa_for_one_item_and_one_invstigation_every_month):
        client = alternate_controlled_and_oa_for_one_item_and_one_invstigation_every_month
        query_body = get_tr_j3_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        assert res['hits']['total'] == 36

    def test_aggregations(self, one_controlled_access_for_one_item_every_month):
        client = one_controlled_access_for_one_item_every_month
        query_body = get_tr_j3_query(make_params(datetime.date(2018, 1, 1),
                                                 datetime.date(2019, 1, 1)))
        res = client.search(index="tests_counter_r5", body=query_body)
        buckets = res['aggregations']['composite_agg']['buckets']
        assert len(buckets) == 1
        assert buckets[0]['key'] == {'parent_proprietary_id': 'bo',
                                     'is_unique': True, 'access_type': 'Controlled',
                                     'is_request': True}
        top_event_source = buckets[0]['event_top_hit']['hits']['hits'][0]['_source']
        assert top_event_source['parent_proprietary_id'] == 'bo'
