import copy
import csv
import datetime
import io

import pytest  # type: ignore

from counter_r5.reports import (
    publisher_ids_to_str,
    tr_j1_query_results_data_to_csv_rows,
    typed_values_to_str,
    make_tr_j1_csv,
    ReportHeader,
    get_counter_query_results_data,
    CounterReportException,
    StandardViewParams,
    make_ir_a1_csv,
    make_tr_j3_csv,
    report_header_to_sushi,
    ReportExceptionInfo,
    group_performances_by_id,
    merge_performances,
    capitalize_keys,
    get_metric_type,
    result_data_to_sushi_title_usage,
    result_data_to_sushi_item_usage,
)
from counter_r5.elasticsearch_query import (
    MonthCount,
    QueryResultData,
)
from counter_r5.tests.test_elasticsearch_query import get_elasticsearch_fixture


def test_publisher_ids_to_str():
    ids = [{'type': 'Proprietary', 'value': 'propid'}, {'type': 'ISNI', 'value': 'isniid'}]
    ids_str = publisher_ids_to_str({'platform': 'erudit', 'publisher_identifiers': ids})
    assert ids_str == 'erudit:propid; ISNI:isniid'


def test_query_results_to_csv_items():
    result = QueryResultData(
        2,
        {
            'parent_title': 'Bioethique',
            'platform': 'Erudit',
            'publisher_name': 'PUL',
            'parent_proprietary_id': '1234',
            'publisher_identifiers': [{'type': 'Proprietary', 'value': 'abcd'}],
            'parent_item_identifiers': [{'type': 'Print_ISSN', 'value': '1234-5678'},
                                        {'type': 'Online_ISSN', 'value': '1111-2222'}, ],
            'parent_uri': 'http://id.erudit.org/1234',
            'is_request': True,
            'is_unique': True,
        },
        [MonthCount(datetime.date(2018, 1, 1), 1), MonthCount(datetime.date(2018, 2, 1), 1)],
    )
    csv_rows = tr_j1_query_results_data_to_csv_rows([result])
    assert len(csv_rows) == 1
    csv_row = list(csv_rows[0].items())
    assert csv_row == [
        ('Title', 'Bioethique'),
        ('Publisher', 'PUL'),
        ('Publisher_ID', 'Erudit:abcd'),
        ('Platform', 'Erudit'),
        ('Proprietary_ID', 'Erudit:1234'),
        ('Print_ISSN', '1234-5678'),
        ('Online_ISSN', '1111-2222'),
        ('URI', 'http://id.erudit.org/1234'),
        ('Metric_Type', 'Unique_Item_Requests'),
        ('Reporting_Period_Total', 2),
        ('Jan-2018', 1),
        ('Feb-2018', 1),
    ]


def test_typed_values_to_str():
    assert typed_values_to_str([('a', '1'), ('b', '2')]) == 'a=1; b=2'


# noinspection PyUnusedLocal
def fake_search(d: dict) -> dict:
    return get_elasticsearch_fixture('tr_j1_result.json')


# noinspection PyUnusedLocal
def fake_search_empty(d: dict) -> dict:
    return get_elasticsearch_fixture('tr_j1_result_empty.json')


# noinspection PyUnusedLocal
def fake_search_ir_a1(d: dict) -> dict:
    return get_elasticsearch_fixture('ir_a1_result.json')


# noinspection PyUnusedLocal
def fake_search_tr_j3(d: dict) -> dict:
    return get_elasticsearch_fixture('tr_j3_result.json')


def test_make_tr_j1_csv():
    f = io.StringIO()
    params = StandardViewParams(
        search=fake_search,
        created=datetime.datetime(2019, 2, 5, 13, 45, 30, 1234),
        created_by='wwwerudit',
        begin_date=datetime.date(2018, 1, 1),
        end_date=datetime.date(2018, 12, 31),
        customer_id='biblav',
        customer_name='Bibliothèque Laval',
        platform='Erudit',
        with_breakdown_by_month=True)
    make_tr_j1_csv(f, params)
    f.seek(0)
    reader = csv.reader(f, 'excel')
    rows = []
    for row in reader:
        rows.append(row)
    assert len(rows) == 16  # header(12) + blank line(1) + header(1) + rows(2)
    assert rows[10] == ['Created', '2019-02-05T13:45:30Z']
    assert rows[12] == []
    assert rows[14][0] == "Bioéthique online"
    assert rows[14][-13:] == ['12'] + ['1'] * 12


def test_make_tr_j1_csv_when_empty():
    f = io.StringIO()
    params = StandardViewParams(
        search=fake_search_empty,
        created=datetime.datetime(2019, 2, 5, 13, 45),
        created_by='wwwerudit',
        begin_date=datetime.date(2015, 1, 1),
        end_date=datetime.date(2015, 12, 31),
        customer_id='biblav',
        customer_name='Bibliothèque Laval',
        platform='Erudit',
        with_breakdown_by_month=True)
    with pytest.raises(CounterReportException) as e:
        make_tr_j1_csv(f, params)
    assert e.match('3030')


def test_make_ir_a1_csv():
    f = io.StringIO()
    params = StandardViewParams(
        search=fake_search_ir_a1,
        created=datetime.datetime(2019, 2, 5, 13, 45),
        created_by='wwwerudit',
        begin_date=datetime.date(2018, 1, 1),
        end_date=datetime.date(2018, 12, 31),
        customer_id='biblav',
        customer_name='Bibliothèque Laval',
        platform='Erudit',
        with_breakdown_by_month=True)
    make_ir_a1_csv(f, params)
    f.seek(0)
    reader = csv.reader(f, 'excel')
    rows = []
    for row in reader:
        rows.append(row)
    assert len(rows) == 16  # header(12) + blank line(1) + header(1) + rows(2)
    assert rows[12] == []
    assert rows[14][0] == "Flesh, Foil, and Authenticity: Reflections on Johann AR Roduit"
    assert rows[14][-13:] == ['12'] + ['1'] * 12


def test_make_tr_j3_csv():
    f = io.StringIO()
    params = StandardViewParams(
        search=fake_search_tr_j3,
        created=datetime.datetime(2019, 2, 5, 13, 45),
        created_by='wwwerudit',
        begin_date=datetime.date(2018, 1, 1),
        end_date=datetime.date(2018, 12, 31),
        customer_id='biblav',
        customer_name='Bibliothèque Laval',
        platform='Erudit',
        with_breakdown_by_month=True)
    make_tr_j3_csv(f, params)
    f.seek(0)
    reader = csv.reader(f, 'excel')
    rows = []
    for row in reader:
        rows.append(row)
    assert len(rows) == 16  # header(12) + blank line(1) + header(1) + rows(2)
    assert rows[12] == []
    assert rows[14][0] == "Bioéthique online"
    assert rows[14][-13:] == ['12'] + ['1'] * 12


class TestGetCounterQueryResultsData:
    def test_raises_exception_if_invalid_dates(self):
        params = StandardViewParams(
            search=lambda d: {},
            created=datetime.datetime(2019, 2, 5, 13, 45),
            created_by='wwwerudit',
            begin_date=datetime.date(2015, 12, 31),
            end_date=datetime.date(2015, 1, 1),
            customer_id='biblav',
            customer_name='Bibliothèque Laval',
            platform='Erudit',
            with_breakdown_by_month=True
        )
        with pytest.raises(CounterReportException) as exc_info:
            get_counter_query_results_data(params, {}, '', '', [], [])
        assert exc_info.match('3020')

    def test_raises_exception_if_connection_error(self):

        # noinspection PyUnusedLocal
        def raise_connection_error(d):
            raise ConnectionError

        params = StandardViewParams(
            search=raise_connection_error,
            created=datetime.datetime(2019, 2, 5, 13, 45),
            created_by='wwwerudit',
            begin_date=datetime.date(2015, 1, 1),
            end_date=datetime.date(2015, 1, 31),
            customer_id='biblav',
            customer_name='Bibliothèque Laval',
            platform='Erudit',
            with_breakdown_by_month=True
        )
        with pytest.raises(CounterReportException) as exc_info:
            get_counter_query_results_data(params, {}, '', '', [], [])
        assert exc_info.match('1000')
        assert 1000 == exc_info.value.header.Exceptions[0].Code


def test_report_header_to_sushi():
    header = ReportHeader(
        Created=datetime.datetime(2019, 1, 2, 11, 15, 30),
        Created_By='erudit',
        Report_ID='TR_J1',
        Report_Name='journals',
        Institution_Name='udm',
        Institution_ID='',
        Metric_Types=[],
        Report_Filters=[],
        Report_Attributes=[],
        Begin_Date=datetime.date(2018, 1, 1),
        End_Date=datetime.date(2018, 2, 1),
    )
    sushi_header = report_header_to_sushi(header)
    assert sushi_header == {
        'Created': '2019-01-02T11:15:30Z',
        'Created_By': 'erudit',
        'Report_ID': 'TR_J1',
        'Report_Name': 'journals',
        'Institution_Name': 'udm',
        'Release': '5',
        'Report_Filters': [{'Name': 'Begin_Date', 'Value': '2018-01-01'},
                           {'Name': 'End_Date', 'Value': '2018-02-01'}]
    }


def test_report_header_to_sushi_with_exceptions():
    header = ReportHeader(
        Created=datetime.datetime(2019, 1, 2, 11, 15, 30),
        Created_By='erudit',
        Report_ID='TR_J1',
        Report_Name='journals',
        Institution_Name='udm',
        Institution_ID='',
        Metric_Types=[],
        Report_Filters=[],
        Report_Attributes=[],
        Begin_Date=datetime.date(2018, 1, 1),
        End_Date=datetime.date(2018, 2, 1),
        Exceptions=[ReportExceptionInfo(2000, 'Fatal', 'errormessage', '')],
    )
    sushi_header = report_header_to_sushi(header)
    assert sushi_header['Exceptions'] == [
        {'Code': 2000, 'Severity': 'Fatal', 'Message': 'errormessage'}
    ]


def test_can_group_performances_by_id():
    flat_list = [
        ('1', {'a': 1, 'Performance': [{'Period': {'Begin_Date': '2018-01-01',
                                                   'End_Date': '2018-02-28'},
                                        'Instance': [{'Metric_Type': 'Total_Item_Requests',
                                                      'Count': 2}]
                                        },
                                       {'Period': {'Begin_Date': '2018-01-01',
                                                   'End_Date': '2018-01-31'},
                                        'Instance': [{'Metric_Type': 'Total_Item_Requests',
                                                      'Count': 1}]
                                        },
                                       {'Period': {'Begin_Date': '2018-02-01',
                                                   'End_Date': '2018-02-28'},
                                        'Instance': [{'Metric_Type': 'Total_Item_Requests',
                                                      'Count': 1}]
                                        }
                                       ]
               }),
        ('1', {'a': 1, 'Performance': [{'Period': {'Begin_Date': '2018-01-01',
                                                   'End_Date': '2018-02-28'},
                                        'Instance': [{'Metric_Type': 'Unique_Item_Requests',
                                                      'Count': 10}]
                                        },
                                       {'Period': {'Begin_Date': '2018-01-01',
                                                   'End_Date': '2018-01-31'},
                                        'Instance': [{'Metric_Type': 'Unique_Item_Requests',
                                                      'Count': 5}]
                                        },
                                       {'Period': {'Begin_Date': '2018-02-01',
                                                   'End_Date': '2018-02-28'},
                                        'Instance': [{'Metric_Type': 'Unique_Item_Requests',
                                                      'Count': 5}]
                                        }
                                       ]
               }),
        ('2', {'a': 2, 'Performance': [{'Period': {'Begin_Date': '2018-01-01',
                                                   'End_Date': '2018-02-28'},
                                        'Instance': [{'Metric_Type': 'Total_Item_Requests',
                                                      'Count': 6}]
                                        },
                                       {'Period': {'Begin_Date': '2018-01-01',
                                                   'End_Date': '2018-01-31'},
                                        'Instance': [{'Metric_Type': 'Total_Item_Requests',
                                                      'Count': 3}]
                                        },
                                       {'Period': {'Begin_Date': '2018-02-01',
                                                   'End_Date': '2018-02-28'},
                                        'Instance': [{'Metric_Type': 'Total_Item_Requests',
                                                      'Count': 3}]
                                        }
                                       ]
               }),
    ]
    grouped = group_performances_by_id(flat_list)
    assert len(grouped) == 2
    assert grouped[0]['Performance'] == [
        {'Period': {'Begin_Date': '2018-01-01',
                    'End_Date': '2018-02-28'},
         'Instance': [{'Metric_Type': 'Total_Item_Requests',
                       'Count': 2},
                      {'Metric_Type': 'Unique_Item_Requests',
                       'Count': 10}
                      ]
         },
        {'Period': {'Begin_Date': '2018-01-01',
                    'End_Date': '2018-01-31'},
         'Instance': [{'Metric_Type': 'Total_Item_Requests',
                       'Count': 1},
                      {'Metric_Type': 'Unique_Item_Requests',
                       'Count': 5}
                      ]
         },
        {'Period': {'Begin_Date': '2018-02-01',
                    'End_Date': '2018-02-28'},
         'Instance': [{'Metric_Type': 'Total_Item_Requests',
                       'Count': 1},
                      {'Metric_Type': 'Unique_Item_Requests',
                       'Count': 5}
                      ]
         }
    ]


def test_can_merge_performances():
    perfs_1 = [{
        'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-01-31'},
        'Instance': [{'Metric_Type': 'Total_Item_Requests', 'Count': 1}]}]
    perfs_2 = [{'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-01-31'},
                'Instance': [{'Metric_Type': 'Total_Item_Investigations', 'Count': 1}]},
               {'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-02-28'},
                'Instance': [{'Metric_Type': 'Unique_Item_Investigations', 'Count': 1}]},
               ]
    backup_perfs_1, backup_perfs_2 = copy.deepcopy(perfs_1), copy.deepcopy(perfs_2)
    assert merge_performances(perfs_1, perfs_2) == [
        {
            'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-01-31'},
            'Instance': [{'Metric_Type': 'Total_Item_Requests', 'Count': 1},
                         {'Metric_Type': 'Total_Item_Investigations', 'Count': 1}]
        },
        {
            'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-02-28'},
            'Instance': [{'Metric_Type': 'Unique_Item_Investigations', 'Count': 1}]
        },
    ]
    # merge_performances should not mutate its inputs
    assert (backup_perfs_1, backup_perfs_2) == (perfs_1, perfs_2)


def test_can_merge_performances_and_remove_duplicate_instances():
    perfs_1 = [
        {
            'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-01-31'},
            'Instance': [{'Metric_Type': 'Total_Item_Requests', 'Count': 1},
                         {'Metric_Type': 'Total_Item_Investigations', 'Count': 1}]},
    ]
    perfs_2 = [{'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-01-31'},
                'Instance': [{'Metric_Type': 'Total_Item_Investigations', 'Count': 1}]},
               {'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-02-28'},
                'Instance': [{'Metric_Type': 'Unique_Item_Investigations', 'Count': 1}]},
               ]
    backup_perfs_1, backup_perfs_2 = copy.deepcopy(perfs_1), copy.deepcopy(perfs_2)
    merged = merge_performances(perfs_1, perfs_2)
    assert merged == [
        {
            'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-01-31'},
            'Instance': [{'Metric_Type': 'Total_Item_Requests', 'Count': 1},
                         {'Metric_Type': 'Total_Item_Investigations', 'Count': 1}]
        },
        {
            'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-02-28'},
            'Instance': [{'Metric_Type': 'Unique_Item_Investigations', 'Count': 1}]
        },
    ]
    # merge_performances should not mutate its inputs
    assert (backup_perfs_1, backup_perfs_2) == (perfs_1, perfs_2)


def test_can_capitalize_keys():
    d = [{'abc': 1, 'def_ghi': 2}]
    assert capitalize_keys(d) == [{'Abc': 1, 'Def_Ghi': 2}]


def test_can_get_metric_type():
    assert get_metric_type({'is_unique': True, 'is_request': True}) == 'Unique_Item_Requests'
    assert get_metric_type({'is_unique': True, 'is_request': False}) == 'Unique_Item_Investigations'
    assert get_metric_type({'is_unique': False, 'is_request': True}) == 'Total_Item_Requests'
    assert get_metric_type({'is_unique': False, 'is_request': False}) == 'Total_Item_Investigations'


def test_can_transform_result_data_to_sushi_title_usage():
    result_data = QueryResultData(
        total_count=123,
        top_event={
            'is_unique': True,
            'is_request': True,
            'parent_proprietary_id': 'idjournal',
            'parent_title': 'journaltitle',
            'parent_item_identifiers': [{'type': 'Proprietary', 'value': 'journaleruditid'}],
            'platform': 'erudit',
            'publisher_name': 'editeur',
            'publisher_identifiers': [{'type': 'Proprietary', 'value': 'pubid'}],
            'year_of_publication': 2018,
            'access_type': 'Controlled',
            'access_method': 'Regular'
        },
        by_month=[MonthCount(datetime.date(2019, 2, 1), 12)]
    )
    title_id, title_usage = result_data_to_sushi_title_usage(datetime.date(2019, 1, 1),
                                                             datetime.date(2019, 2, 1),
                                                             result_data)
    assert title_id == 'idjournal'
    assert title_usage['Performance'] == [
        {'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-02-01'},
         'Instance': [{'Metric_Type': 'Unique_Item_Requests',
                       'Count': 123}]},
        {'Period': {'Begin_Date': '2019-02-01', 'End_Date': '2019-02-28'},
         'Instance': [{'Metric_Type': 'Unique_Item_Requests',
                       'Count': 12}]},
    ]
    assert title_usage['Title'] == 'journaltitle'
    assert title_usage['Item_ID'] == [{'Type': 'Proprietary', 'Value': 'journaleruditid'}]
    assert title_usage['Platform'] == 'erudit'
    assert title_usage['Publisher'] == 'editeur'


def test_can_transform_result_data_to_sushi_item_usage():
    result_data = QueryResultData(
        total_count=123,
        top_event={
            'is_unique': True,
            'is_request': True,
            'proprietary_id': 'iderudit',
            'title': 'articletitle',
            'parent_proprietary_id': 'idjournal',
            'parent_title': 'journaltitle',
            'parent_item_identifiers': [{'type': 'Proprietary', 'value': 'journaleruditid'}],
            'item_identifiers': [{'type': 'Proprietary', 'value': 'eruditid'}],
            'item_contributors': [{'type': 'Author', 'value': 'author1'}],
            'publication_date': '2019-01-01',
            'platform': 'erudit',
            'publisher_name': 'editeur',
            'publisher_identifiers': [{'type': 'Proprietary', 'value': 'pubid'}],
            'year_of_publication': 2018,
            'access_type': 'Controlled',
            'access_method': 'Regular'
        },
        by_month=[MonthCount(datetime.date(2019, 2, 1), 12)]
    )
    title_id, title_usage = result_data_to_sushi_item_usage(datetime.date(2019, 1, 1),
                                                            datetime.date(2019, 2, 1),
                                                            result_data)
    assert title_id == 'iderudit'
    assert title_usage['Performance'] == [
        {'Period': {'Begin_Date': '2019-01-01', 'End_Date': '2019-02-01'},
         'Instance': [{'Metric_Type': 'Unique_Item_Requests',
                       'Count': 123}]},
        {'Period': {'Begin_Date': '2019-02-01', 'End_Date': '2019-02-28'},
         'Instance': [{'Metric_Type': 'Unique_Item_Requests',
                       'Count': 12}]},
    ]
    assert title_usage['Item'] == 'articletitle'
    assert title_usage['Item_ID'] == [{'Type': 'Proprietary', 'Value': 'eruditid'}]
    assert title_usage['Platform'] == 'erudit'
    assert title_usage['Publisher'] == 'editeur'
    assert title_usage['Item_Dates'] == [{'Type': 'Publication_Date', 'Value': '2019-01-01'}]
