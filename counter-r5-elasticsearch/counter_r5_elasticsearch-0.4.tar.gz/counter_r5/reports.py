import csv
import datetime
import json

from dateutil import (
    rrule,
    relativedelta,
)
from collections import OrderedDict
from typing import (
    List,
    Optional,
    Callable,
    NamedTuple,
    Dict,
    IO,
    Tuple,
    Any,
    Iterable,
)

from counter_r5.elasticsearch_query import (
    SearchFunction,
    MonthCount,
    QueryResultData,
    get_composite_query_results_data,
    build_usage_query,
    format_date,
    extract_stats_by_month,
    MONTHS,
)

SEP = '; '

REPORT_NAMES = {
    'TR_J1': 'Journal Requests (Excluding OA_Gold)',
    'TR_J3': 'Journal Usage by Access Type',
    'IR_A1': 'Journal Article Requests',
}


class StandardViewParams(NamedTuple):
    """Params for all standard views (eg: TR_J1, TR_J3), master reports will need more
    parameters. """
    search: SearchFunction
    created: datetime.datetime
    created_by: str
    begin_date: datetime.date
    end_date: datetime.date
    customer_id: str
    customer_name: str
    platform: str
    with_breakdown_by_month: bool


class ReportExceptionInfo(NamedTuple):
    Code: int
    Severity: str
    Message: str
    Data: str


class ReportHeader(NamedTuple):
    Created: datetime.datetime
    Created_By: str
    Report_ID: str
    Report_Name: str
    Institution_Name: str
    Institution_ID: str
    Metric_Types: List[str]
    Report_Filters: List[Tuple[str, str]]
    Report_Attributes: List[Tuple[str, str]]
    Begin_Date: datetime.date
    End_Date: datetime.date
    Release: str = '5'
    Exceptions: List[ReportExceptionInfo] = []


class CounterQueryResults(NamedTuple):
    header: ReportHeader
    results_data: List[QueryResultData]


def fast_copy(d: dict) -> dict:
    return json.loads(json.dumps(d))


def make_exception_message(exception):
    message = f'{exception.Code}: {exception.Message}'
    if exception.Data:
        message += f' ({exception.Data})'
    return message


class CounterReportException(Exception):
    def __init__(self, header: ReportHeader, exception: ReportExceptionInfo):
        self.header = header._replace(Exceptions=header.Exceptions + [exception])
        super().__init__(make_exception_message(exception))


def list_months_fields(begin_date: datetime.date, end_date: datetime.date) -> List[str]:
    first_day = begin_date.replace(day=1)
    month_dates = []
    start_datetime = datetime.datetime(first_day.year, first_day.month, first_day.day)
    end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day)
    for month_date in rrule.rrule(rrule.MONTHLY, start_datetime, until=end_datetime):
        month_dates.append((month_date.month, month_date.year))
    return [f'{MONTHS[month_number - 1]}-{year}' for month_number, year in month_dates]


def make_report_header(params: StandardViewParams, report_id: str, report_name: str,
                       metric_types: List[str],
                       report_filters: List[Tuple[str, str]]) -> ReportHeader:
    return ReportHeader(
        Created=params.created,
        Created_By=params.created_by,
        Report_ID=report_id,
        Report_Name=report_name,
        Institution_Name=params.customer_name,
        Institution_ID=f'{params.platform}:{params.customer_id}',
        Metric_Types=metric_types,
        Report_Filters=report_filters,
        Report_Attributes=[],
        Begin_Date=params.begin_date,
        End_Date=params.end_date,
    )


def get_tr_j1_field_names(params: StandardViewParams) -> List[str]:
    field_names = [
        'Title', 'Publisher', 'Publisher_ID', 'Platform', 'Proprietary_ID', 'Print_ISSN',
        'Online_ISSN', 'URI', 'Metric_Type', 'Reporting_Period_Total'
    ]
    if params.with_breakdown_by_month:
        field_names.extend(list_months_fields(params.begin_date, params.end_date))
    return field_names


def get_ir_a1_field_names(params: StandardViewParams) -> List[str]:
    field_names = [
        'Item', 'Publisher', 'Publisher_ID', 'Platform', 'Authors', 'Publication_Date',
        'Article_Version', 'DOI', 'Proprietary_ID', 'Print_ISSN', 'Online_ISSN', 'URI',
        'Parent_Title', 'Parent_Authors', 'Parent_Article_Version', 'Parent_DOI',
        'Parent_Proprietary_ID', 'Parent_Print_ISSN', 'Parent_Online_ISSN', 'Parent_URI',
        'Access_Type', 'Metric_Type', 'Reporting_Period_Total'
    ]
    if params.with_breakdown_by_month:
        field_names.extend(list_months_fields(params.begin_date, params.end_date))
    return field_names


def get_tr_j3_field_names(params: StandardViewParams) -> List[str]:
    field_names = [
        'Title', 'Publisher', 'Publisher_ID', 'Platform', 'DOI', 'Proprietary_ID', 'Print_ISSN',
        'Online_ISSN', 'URI', 'Access_Type', 'Metric_Type', 'Reporting_Period_Total']
    if params.with_breakdown_by_month:
        field_names.extend(list_months_fields(params.begin_date, params.end_date))
    return field_names


def get_counter_query_results_data(params: StandardViewParams, query_body: dict, report_id: str,
                                   report_name: str, metric_types: List[str],
                                   report_filters: List[Tuple[str, str]]) -> CounterQueryResults:
    header = make_report_header(params, report_id, report_name, metric_types, report_filters)
    if header.End_Date <= header.Begin_Date:
        raise CounterReportException(
            header,
            ReportExceptionInfo(
                3020, 'Error', 'Invalid date arguments',
                f'Begin_Date={header.Begin_Date};End_Date={header.End_Date}'
            )
        )
    try:
        query_results = get_composite_query_results_data(params.search, query_body)
    except ConnectionError as e:
        raise CounterReportException(
            header, ReportExceptionInfo(1000, 'Fatal', 'Service unavailable', str(e)))
    if len(query_results.composite_aggregation_data) == 0:
        raise CounterReportException(
            header,
            ReportExceptionInfo(
                3030, 'Error', 'No Usage Available for Requested Dates',
                f'Begin_Date={header.Begin_Date};End_Date={header.End_Date}'
            )
        )

    return CounterQueryResults(header, query_results.composite_aggregation_data)


def get_tr_j1_data(params: StandardViewParams) -> CounterQueryResults:
    query_body = get_tr_j1_query(params)
    return get_counter_query_results_data(
        params, query_body, 'TR_J1', REPORT_NAMES['TR_J1'],
        ['Total_Item_Requests', 'Unique_Item_Requests'],
        [('Data_Type', 'Journal'), ('Access_Type', 'Controlled'), ('Access_Method', 'Regular')]
    )


def get_ir_a1_data(params: StandardViewParams) -> CounterQueryResults:
    query_body = get_ir_a1_query(params)
    return get_counter_query_results_data(
        params, query_body, 'IR_A1', REPORT_NAMES['IR_A1'],
        ['Total_Item_Requests', 'Unique_Item_Requests'],
        [('Data_Type', 'Article'), ('Parent_Data_Type', 'Journal'), ('Access_Method', 'Regular')])


def get_tr_j3_data(params: StandardViewParams) -> CounterQueryResults:
    query_body = get_tr_j3_query(params)
    return get_counter_query_results_data(
        params, query_body, 'TR_J3', REPORT_NAMES['TR_J3'],
        ['Total_Item_Requests', 'Unique_Item_Requests', 'Total_Item_Investigations',
         'Unique_Item_Investigations'],
        [('Data_Type', 'Journal'), ('Access_Method', 'Regular')])


def get_tr_j1_query(params: StandardViewParams) -> dict:
    return build_r5_query(
        params,
        ['is_unique', 'parent_proprietary_id'],
        [("access_type", "Controlled"),
         ("is_request", True)],
    )


def get_ir_a1_query(params: StandardViewParams) -> dict:
    return build_r5_query(
        params,
        ['proprietary_id', 'is_unique', 'access_type'],
        [("is_request", True)],
    )


def get_tr_j3_query(params: StandardViewParams) -> dict:
    return build_r5_query(
        params,
        ["parent_proprietary_id", "is_unique", "access_type", "is_request"],
    )


def build_r5_query(params: StandardViewParams, aggregation_fields: List[str],
                   additional_must_terms: Optional[Iterable[Tuple[str, Any]]] = None) -> dict:
    must_terms = [
        ("institution_identifiers.value", params.customer_id),
        ("institution_identifiers.type", "Proprietary"),
        ("platform", params.platform),
    ]
    must_terms.extend(additional_must_terms or [])

    return build_usage_query(params.begin_date, params.end_date, must_terms,
                             aggregation_fields, [], params.with_breakdown_by_month)


def publisher_ids_to_str(event: dict) -> str:
    publisher_identifiers = event.get('publisher_identifiers', [])
    publisher_ids = []
    for pub_id in publisher_identifiers:
        pub_id_type = pub_id['type']
        if pub_id_type == 'Proprietary':
            pub_id_type = event['platform']
        publisher_ids.append(f"{pub_id_type}:{pub_id['value']}")
    publisher_ids_str = SEP.join(publisher_ids)
    return publisher_ids_str


def extract_identifier(identifiers: List[Dict[str, str]], id_type: str, default: str = None) -> str:
    ids_dict = {d['type']: d['value'] for d in identifiers}
    if default is None:
        return ids_dict[id_type]
    else:
        return ids_dict.get(id_type, default)


def tr_j1_query_results_data_to_csv_rows(results: List[QueryResultData]) -> List[OrderedDict]:
    items = []
    for result in results:
        event = result.top_event
        is_unique = event['is_unique']
        metric_type = "Unique_Item_Requests" if is_unique else "Total_Item_Requests"
        item = OrderedDict(
            Title=event['parent_title'],
            Publisher=event['publisher_name'],
            Publisher_ID=publisher_ids_to_str(event),
            Platform=event['platform'],
            Proprietary_ID=f"{event['platform']}:{event['parent_proprietary_id']}",
            Print_ISSN=extract_identifier(event['parent_item_identifiers'], 'Print_ISSN', ''),
            Online_ISSN=extract_identifier(event['parent_item_identifiers'], 'Online_ISSN'),
            URI=event['parent_uri'],
            Metric_Type=metric_type,
            Reporting_Period_Total=result.total_count,
        )
        item.update(extract_stats_by_month(result.by_month))
        items.append(item)
    return items


def format_contributors(contributors: List[dict]) -> str:
    return SEP.join([f'{c["name"]}({c["identifier"]})' for c in contributors])


def ir_a1_query_results_data_to_csv_rows(results: List[QueryResultData]) -> List[OrderedDict]:
    items = []
    for result in results:
        event = result.top_event
        is_unique = event['is_unique']
        metric_type = "Unique_Item_Requests" if is_unique else "Total_Item_Requests"
        authors = format_contributors(event.get('item_contributors', []))
        parent_authors = format_contributors(event.get('parent_item_contributors', []))
        item = OrderedDict(
            Item=event['title'],
            Publisher=event['publisher_name'],
            Publisher_ID=publisher_ids_to_str(event),
            Platform=event['platform'],
            Authors=authors,
            Publication_Date=event['publication_date'],
            Article_Version='VoR',  # event['article_version'],
            DOI=event.get('doi', ''),
            Proprietary_ID=f"{event['platform']}:{event['proprietary_id']}",
            Print_ISSN=extract_identifier(event['item_identifiers'], 'Print_ISSN', ''),
            Online_ISSN=extract_identifier(event['item_identifiers'], 'Online_ISSN', ''),
            URI=event['uri'],
            Parent_Title=event['parent_title'],
            Parent_Authors=parent_authors,
            Parent_Article_Version='VoR',
            Parent_DOI=event.get('parent_doi', ''),
            Parent_Proprietary_ID=event['parent_proprietary_id'],
            Parent_Print_ISSN=extract_identifier(
                event['parent_item_identifiers'], 'Print_ISSN', ''),
            Parent_Online_ISSN=extract_identifier(event['parent_item_identifiers'], 'Online_ISSN',
                                                  ''),
            Parent_URI=event['parent_uri'],
            Access_Type=event['access_type'],
            Metric_Type=metric_type,
            Reporting_Period_Total=result.total_count,
        )
        item.update(extract_stats_by_month(result.by_month))
        items.append(item)
    return items


def tr_j3_query_results_data_to_csv_rows(results: List[QueryResultData]) -> List[OrderedDict]:
    items = []
    for result in results:
        event = result.top_event
        metric_type = get_metric_type(event)
        item = OrderedDict(
            Title=event['parent_title'],
            Publisher=event['publisher_name'],
            Publisher_ID=publisher_ids_to_str(event),
            Platform=event['platform'],
            DOI=event.get('doi', ''),
            Proprietary_ID=f"{event['platform']}:{event['parent_proprietary_id']}",
            Print_ISSN=extract_identifier(event['parent_item_identifiers'], 'Print_ISSN', ''),
            Online_ISSN=extract_identifier(event['parent_item_identifiers'], 'Online_ISSN', ''),
            URI=event['parent_uri'],
            Access_Type=event['access_type'],
            Metric_Type=metric_type,
            Reporting_Period_Total=result.total_count,
        )
        item.update(extract_stats_by_month(result.by_month))
        items.append(item)
    return items


def get_metric_type(event):
    is_unique = event['is_unique']
    is_request = event['is_request']
    if is_request:
        metric_type = "Unique_Item_Requests" if is_unique else "Total_Item_Requests"
    else:
        metric_type = "Unique_Item_Investigations" if is_unique else "Total_Item_Investigations"
    return metric_type


def typed_values_to_str(values: List[Tuple[str, str]]) -> str:
    return SEP.join(f'{t}={v}' for t, v in values)


def write_csv_header(csv_writer, header: ReportHeader) -> None:
    exceptions = SEP.join([make_exception_message(e) for e in header.Exceptions])
    reporting_period = [('Begin_Date', format_date(header.Begin_Date)),
                        ('End_Date', format_date(header.End_Date))]
    csv_writer.writerow(['Report_Name', header.Report_Name])
    csv_writer.writerow(['Report_ID', header.Report_ID])
    csv_writer.writerow(['Release', header.Release])
    csv_writer.writerow(['Institution_Name', header.Institution_Name])
    csv_writer.writerow(['Institution_ID', header.Institution_ID])
    csv_writer.writerow(['Metric_Types', SEP.join(header.Metric_Types)])
    csv_writer.writerow(['Report_Filters', typed_values_to_str(header.Report_Filters)])
    csv_writer.writerow(['Report_Attributes', typed_values_to_str(header.Report_Attributes)])
    csv_writer.writerow(['Exceptions', exceptions])
    csv_writer.writerow(['Reporting_Period', typed_values_to_str(reporting_period)])
    # noinspection PyArgumentList
    csv_writer.writerow(['Created', header.Created.isoformat(timespec='seconds') + 'Z'])
    csv_writer.writerow(['Created_By', header.Created_By])


def write_counter_csv(f: IO[str], header: ReportHeader, field_names: List[str],
                      rows: List[OrderedDict]) -> None:
    header_writer = csv.writer(f, 'excel')
    write_csv_header(header_writer, header)
    header_writer.writerow([])
    rows_writer = csv.DictWriter(f, field_names, dialect='excel')
    rows_writer.writeheader()
    rows_writer.writerows(rows)


def make_tr_j1_csv(f: IO[str], params: StandardViewParams) -> None:
    field_names = get_tr_j1_field_names(params)
    results = get_tr_j1_data(params)
    rows = tr_j1_query_results_data_to_csv_rows(results.results_data)
    write_counter_csv(f, results.header, field_names, rows)


def make_ir_a1_csv(f: IO[str], params: StandardViewParams) -> None:
    field_names = get_ir_a1_field_names(params)
    results = get_ir_a1_data(params)
    rows = ir_a1_query_results_data_to_csv_rows(results.results_data)
    write_counter_csv(f, results.header, field_names, rows)


def make_tr_j3_csv(f: IO[str], params: StandardViewParams) -> None:
    field_names = get_tr_j3_field_names(params)
    results = get_tr_j3_data(params)
    rows = tr_j3_query_results_data_to_csv_rows(results.results_data)
    write_counter_csv(f, results.header, field_names, rows)


def make_csv_report(report_code: str, f: IO[str], params: StandardViewParams) -> None:
    try:
        if report_code == 'TR_J1':
            make_tr_j1_csv(f, params)
        elif report_code == 'IR_A1':
            make_ir_a1_csv(f, params)
        elif report_code == 'TR_J3':
            make_tr_j3_csv(f, params)
        else:
            header = make_report_header(params, report_code, '', [], [])
            raise CounterReportException(header, ReportExceptionInfo(3000, 'Error',
                                                                     'Report Not Supported', ''))
    except CounterReportException as e:
        header_writer = csv.writer(f, 'excel')
        write_csv_header(header_writer, e.header)


def report_header_to_sushi(header: ReportHeader) -> Dict[str, object]:
    sushi_header = {
        'Created': header.Created.isoformat() + 'Z',
        'Created_By': header.Created_By,
        'Report_ID': header.Report_ID,
        'Report_Name': header.Report_Name,
        'Release': header.Release,
        'Institution_Name': header.Institution_Name,
        'Report_Filters': [{'Name': 'Begin_Date', 'Value': format_date(header.Begin_Date)},
                           {'Name': 'End_Date', 'Value': format_date(header.End_Date)}],
    }
    if header.Exceptions:
        sushi_header['Exceptions'] = exceptions = []
        for exception in header.Exceptions:
            except_dict = {
                'Code': exception.Code,
                'Severity': exception.Severity,
                'Message': exception.Message,
            }
            if exception.Data:
                except_dict['Data'] = exception.Data
            exceptions.append(except_dict)
    return sushi_header


def sushi_period(begin_date: datetime.date, end_date: datetime.date) -> dict:
    return {'Begin_Date': format_date(begin_date), 'End_Date': format_date(end_date)}


def capitalize_keys(dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result_dicts = []
    for d in dicts:
        capitalized_dict = {}
        for key, value in d.items():
            capitalized_key = '_'.join(w.capitalize() for w in key.split('_'))
            capitalized_dict[capitalized_key] = value
        result_dicts.append(capitalized_dict)
    return result_dicts


def make_sushi_performance(begin_date, end_date, metric_type, total):
    return {'Period': sushi_period(begin_date, end_date),
            'Instance': [{'Metric_Type': metric_type, 'Count': total}]}


def month_counts_to_performance(by_month: Optional[List[MonthCount]],
                                metric_type: str) -> List[Dict[str, Any]]:
    performance = []
    if by_month:
        months = [month for month in by_month if month.hits]
        for month in months:
            first_day = month.month
            last_day = month.month + relativedelta.relativedelta(months=1, days=-1)
            performance.append(
                make_sushi_performance(first_day, last_day, metric_type, month.hits))
    return performance


def result_data_to_sushi_title_usage(begin_date: datetime.date, end_date: datetime.date,
                                     result_data: QueryResultData) -> Tuple[str, dict]:
    """Return a tuple of (title id, title_usage) where title_usage is a dict that conforms to
    COUNTER_title_usage in the COUNTER_SUSHI schema.
    """
    event = result_data.top_event
    total = result_data.total_count
    metric_type = get_metric_type(event)
    performance = [make_sushi_performance(begin_date, end_date, metric_type, total)]
    performance.extend(month_counts_to_performance(result_data.by_month, metric_type))
    title_usage = {
        'Title': event['parent_title'],
        'Item_ID': capitalize_keys(event['parent_item_identifiers']),
        'Platform': event['platform'],
        'Publisher': event['publisher_name'],
        'Publisher_ID': capitalize_keys(event['publisher_identifiers']),
        'Data_Type': 'Journal',
        'Section_Type': 'Article',
        'Access_Type': event['access_type'],
        'Access_Method': event['access_method'],
        'Performance': performance,
    }
    if 'year_of_publication' in event:
        title_usage['YOP'] = event['year_of_publication']

    return event['parent_proprietary_id'], title_usage


def result_data_to_sushi_item_usage(begin_date: datetime.date, end_date: datetime.date,
                                    result_data: QueryResultData) -> Tuple[str, dict]:
    """Return a tuple of (title id, title_usage) where title_usage is a dict that conforms to
    COUNTER_title_usage in the COUNTER_SUSHI schema.
    """
    event = result_data.top_event
    total = result_data.total_count
    metric_type = get_metric_type(event)
    performance = [
        make_sushi_performance(begin_date, end_date, metric_type, total)
    ]
    performance.extend(month_counts_to_performance(result_data.by_month, metric_type))
    item_usage = {
        'Item': event['title'] or '-',
        'Item_ID': capitalize_keys(event['item_identifiers']),
        'Item_Contributors': capitalize_keys(event['item_contributors']),
        'Item_Dates': [{'Type': 'Publication_Date', 'Value': event['publication_date']}],
        'Platform': event['platform'],
        'Publisher': event['publisher_name'],
        'Publisher_ID': capitalize_keys(event['publisher_identifiers']),
        'Item_Parent': [{
            'Item_ID': capitalize_keys(event['parent_item_identifiers']),
            'Item_Name': event['parent_title'],
            'Data_Type': 'Journal',
        }],
        'Data_Type': 'Article',
        'Access_Type': event['access_type'],
        'Access_Method': event['access_method'],
        'Performance': performance,
    }
    if 'year_of_publication' in event:
        item_usage['YOP'] = event['year_of_publication']

    return event['proprietary_id'], item_usage


def period_key(performance: dict) -> Tuple[str, str]:
    period = performance['Period']
    return period['Begin_Date'], period['End_Date']


def merge_performances(list1: List[Dict], list2: List[dict]) -> List[Dict]:
    by_period = {period_key(performance): fast_copy(performance) for performance in list1}
    for performance_to_add in list2:
        key = period_key(performance_to_add)
        try:
            performance = by_period[key]
        except KeyError:
            by_period[key] = fast_copy(performance_to_add)
            continue
        instances = performance['Instance']
        for i in performance_to_add['Instance']:
            if i not in instances:
                instances.append(i)
    return list(by_period.values())


def group_performances_by_id(flat_title_usages: List[Tuple[str, dict]]) -> List[Dict]:
    grouped: Dict[str, dict] = {}
    for item_id, usage in flat_title_usages:
        try:
            append_to = grouped[item_id]
        except KeyError:
            grouped[item_id] = fast_copy(usage)
            continue
        append_to['Performance'] = merge_performances(append_to['Performance'],
                                                      usage['Performance'])
    return list(grouped.values())


SushiUsageMappingFunction = Callable[[datetime.date, datetime.date, QueryResultData],
                                     Tuple[str, dict]]


def query_results_data_to_sushi(results: CounterQueryResults,
                                mapping_function: SushiUsageMappingFunction) -> dict:
    header = report_header_to_sushi(results.header)
    # this gives a flat list of usages (csv-like)
    flat_title_usages = [mapping_function(results.header.Begin_Date,
                                          results.header.End_Date, result_data)
                         for result_data in results.results_data]
    # but COUNTER_SUSHI requires that results are grouped by ID, with all metric types count
    # in the performance field
    title_usages = group_performances_by_id(flat_title_usages)
    return {
        'Report_Header': header,
        'Report_Items': title_usages,
    }


def make_tr_j1_sushi(params: StandardViewParams) -> dict:
    results = get_tr_j1_data(params)
    return query_results_data_to_sushi(results, result_data_to_sushi_title_usage)


def make_tr_j3_sushi(params: StandardViewParams) -> dict:
    results = get_tr_j3_data(params)
    return query_results_data_to_sushi(results, result_data_to_sushi_title_usage)


def make_ir_a1_sushi(params: StandardViewParams) -> dict:
    results = get_ir_a1_data(params)
    return query_results_data_to_sushi(results, result_data_to_sushi_item_usage)


def get_report_as_sushi_data(report_code: str, params: StandardViewParams) -> Dict[str, Any]:
    try:
        if report_code == 'TR_J1':
            data = make_tr_j1_sushi(params)
        elif report_code == 'IR_A1':
            data = make_ir_a1_sushi(params)
        elif report_code == 'TR_J3':
            data = make_tr_j3_sushi(params)
        else:
            header = make_report_header(params, report_code, '', [], [])
            raise CounterReportException(header, ReportExceptionInfo(3000, 'Error',
                                                                     'Report Not Supported', ''))
        return data

    except CounterReportException as e:
        sushi_header = report_header_to_sushi(e.header)
        return {'Report_Header': sushi_header, 'Report_Items': []}


def get_error_response_as_sushi(params: StandardViewParams, report_id: str,
                                exception: ReportExceptionInfo) -> dict:
    report_name = REPORT_NAMES[report_id]
    header = make_report_header(params, report_id, report_name, [], [])
    header = header._replace(Exceptions=[exception])
    sushi_header = report_header_to_sushi(header)
    return {'Report_Header': sushi_header, 'Report_Items': []}
