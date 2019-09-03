import datetime
import json
import random
from pathlib import Path
from typing import (
    List,
    Dict,
    Any,
)

from elasticsearch.helpers import bulk  # type: ignore
from elasticsearch import (  # type: ignore
    Elasticsearch,
    NotFoundError,
)
from elasticsearch.client import IndicesClient  # type: ignore


# 1 access one item every month for one year
# 2 access once unique, once not
# 3 access once double-click, once not
# 4 access one different item of one title every month for one year
from counter_r5.reports import (
    get_tr_j1_query,
    StandardViewParams,
    get_ir_a1_query,
    get_tr_j3_query,
)
from counter_r5.elasticsearch_query import SearchFunction


def get_client() -> Elasticsearch:
    return Elasticsearch([{"host": "127.0.0.1", "port": 9200}])


def get_mappings():
    root_path = Path(__file__).parent.parent.parent
    path = root_path / "schemas" / "elasticsearch_mapping.json"
    with open(path, 'r') as f:
        return json.load(f)


def create_index(client: Elasticsearch, body: dict) -> None:
    indices = IndicesClient(client)
    try:
        indices.delete("tests_counter_r5")
    except NotFoundError:
        pass
    indices.create("tests_counter_r5", body=body)


def destroy_index(client: Elasticsearch) -> None:
    indices = IndicesClient(client)
    indices.delete("tests_counter_r5")


def index_records(client: Elasticsearch, records: List[dict],
                  index_name: str = "tests_counter_r5") -> None:
    ops = []
    for record in records:
        op = {'_index': index_name, '_type': 'usage_events'}
        op.update(record)
        ops.append(op)
    bulk(client, ops)
    client.indices.refresh(index=index_name)


def build_record(timestamp: datetime.datetime, proprietary_id: str, institution_id: str, title: str,
                 access_type: str, parent_proprietary_id: str, **kwargs) -> dict:
    ip = kwargs.get('ip', '{}.{}.{}.{}'.format(random.randint(0, 256),
                                               random.randint(0, 256),
                                               random.randint(0, 256),
                                               random.randint(0, 256)))
    year_of_publication = kwargs.get("year_of_publication", "2019")
    is_unique = kwargs.get("is_unique", True)
    is_request = kwargs.get("is_request", True)
    is_double_click = kwargs.get("is_double_click", False)
    status_code = kwargs.get("status_code", "200")
    user_agent = kwargs.get("user_agent", 'mozilla')
    publisher_proprietary_id = kwargs.get("publisher_proprietary_id", "")
    parent_title = kwargs.get("parent_title", "")
    publisher = kwargs.get("publisher", "PUL")
    publication_date = kwargs.get("publication_date")
    doi = kwargs.get("doi", "")
    data_type = kwargs.get("data_type", "Article")
    return {
        "timestamp": timestamp.strftime("%Y%m%dT%H%M%S.%f")[:-3] + 'Z',
        "ip": ip,
        "proprietary_id": proprietary_id,
        "institution_identifiers": [{'type': 'Proprietary', 'value': institution_id}],
        "platform": "erudit",
        "section_type": "Article",
        "year_of_publication": year_of_publication,
        "uri": "https://id.erudit.org/iderudit/{}".format(proprietary_id),
        "parent_uri": "https://id.erudit.org/iderudit/{}".format(parent_proprietary_id),
        "title": title,
        "item_contributors": [{"type": "Author", "name": "Virginia Woolf",
                               "identifier": "orcid:0000-0001-2345-6789"}],
        "access_type": access_type,
        "protocol": "https",
        "http_method": "GET",
        "size": 4096,
        "status_code": status_code,
        "is_unique": is_unique,
        "is_request": is_request,
        "is_double_click": is_double_click,
        "user_agent": user_agent,
        "publisher_proprietary_id": publisher_proprietary_id,
        "parent_proprietary_id": parent_proprietary_id,
        "parent_title": parent_title,
        "publisher_name": publisher,
        "publication_date": publication_date,
        "data_type": data_type,
        "doi": doi,
        "article_version": "VoR",
        "access_method": "Regular",
        "publisher_identifiers": [{'type': 'Proprietary', 'value': publisher_proprietary_id}],
        "parent_item_identifiers": [{'type': 'Proprietary', 'value': parent_proprietary_id},
                                    {'type': 'Print_ISSN', 'value': '1234-5678'},
                                    {'type': 'Online_ISSN', 'value': '4321-8765'},
                                    {'type': 'ISBN', 'value': '0000-0000'}, ],
        'parent_data_type': 'Journal',
        'parent_doi': 'parent_doi',
        "item_identifiers": [{'type': 'Proprietary', 'value': proprietary_id},
                             {'type': 'Print_ISSN', 'value': '0000-5678'},
                             {'type': 'Online_ISSN', 'value': '4321-0000'},
                             {'type': 'ISBN', 'value': '0000-0000'}, ],
    }


def build_two_thousand_journals() -> List[dict]:
    records = []
    for i in range(0, 2000):
        records.append(
            build_record(
                timestamp=datetime.datetime(2018, 1, 12, 13, 45, 15, 123),
                proprietary_id='{}ar'.format(i),
                institution_id='univlaval',
                title="Article n{}".format(i),
                access_type="Controlled",
                parent_proprietary_id="j{}".format(i),
                is_request=True,
            ))
    return records


def build_one_access_every_month_for_one_item(
        controlled: bool = True, institution_id: str = 'univlaval', is_request=True):
    records = []
    for month in range(1, 13):
        timestamp = datetime.datetime(2018, month, 12, 13, 45, 15, 123)
        record = build_record(
            timestamp=timestamp,
            proprietary_id='1044608ar',
            institution_id=institution_id,
            title="Flesh, Foil, and Authenticity: Reflections on Johann AR Roduit",
            access_type="Controlled" if controlled else "OA_Gold",
            parent_proprietary_id="bo",
            is_request=is_request,
        )
        records.append(record)
    return records


def build_one_unique_access_one_not_unique_every_month_for_one_item(
        controlled: bool = True, institution_id: str = 'univlaval'):
    records = []
    for month in range(1, 13):
        timestamp = datetime.datetime(2018, month, 12, 13, 45, 15, 123)
        record_data: Dict[str, Any] = dict(
            timestamp=timestamp,
            proprietary_id='1044608ar',
            institution_id=institution_id,
            title="Flesh, Foil, and Authenticity: Reflections on Johann AR Roduit",
            access_type="Controlled" if controlled else "OA_Gold",
            parent_proprietary_id="bo",
            publisher_proprietary_id='PUL',
            parent_title="Bioéthique online",
        )
        records.append(build_record(**record_data))
        record_data['is_unique'] = False
        record_data['timestamp'] = record_data['timestamp'] + datetime.timedelta(minutes=15)
        records.append(build_record(**record_data))
    return records


def dump_query(query_body, filename):
    client_ = get_client()
    create_index(client_, get_mappings())
    try:
        index_records(client_, build_one_unique_access_one_not_unique_every_month_for_one_item())
        res = client_.search(index="tests_counter_r5", body=query_body)
        try:
            del res['aggregations']['composite_agg']['after_key']
        except KeyError:
            pass

        with open(Path(__file__).parent / filename, 'wb') as f:
            f.write(json.dumps(res).encode('utf-8'))
    finally:
        destroy_index(client_)


def make_params(begin_date: datetime.date, end_date: datetime.date,
                search_fn: SearchFunction = lambda d: d) -> StandardViewParams:
    return StandardViewParams(search=search_fn,
                              created=datetime.datetime.now(),
                              created_by='Érudit',
                              begin_date=begin_date,
                              end_date=end_date,
                              customer_id='univlaval',
                              customer_name='Université Laval',
                              platform='erudit',
                              with_breakdown_by_month=True)


def dump_results_fixtures():
    dump_query(get_tr_j1_query(make_params(datetime.date(2018, 1, 1), datetime.date(2019, 1, 1))),
               'tr_j1_result.json')
    dump_query(get_tr_j1_query(make_params(datetime.date(2015, 1, 1), datetime.date(2016, 1, 1))),
               'tr_j1_result_empty.json')
    dump_query(get_ir_a1_query(make_params(datetime.date(2018, 1, 1), datetime.date(2019, 1, 1))),
               'ir_a1_result.json')
    dump_query(get_tr_j3_query(make_params(datetime.date(2018, 1, 1), datetime.date(2019, 1, 1))),
               'tr_j3_result.json')
