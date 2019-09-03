import pytest  # type: ignore

from .build_fixtures import (
    get_client,
    get_mappings,
    create_index,
    destroy_index,
    build_one_access_every_month_for_one_item,
    build_one_unique_access_one_not_unique_every_month_for_one_item,
    index_records,
    build_two_thousand_journals,
)


@pytest.fixture(scope="module")
def elasticsearch_index():
    client = get_client()
    body = get_mappings()
    create_index(client, body)
    yield client
    destroy_index(client)


@pytest.fixture
def elasticsearch_client(elasticsearch_index):
    yield elasticsearch_index
    elasticsearch_index.delete_by_query("tests_counter_r5", body={"query": {"match_all": {}}})


@pytest.fixture
def one_controlled_access_for_one_item_every_month(elasticsearch_client):
    index_records(elasticsearch_client, build_one_access_every_month_for_one_item())
    return elasticsearch_client


@pytest.fixture
def one_access_for_one_item_every_month_two_institutions(elasticsearch_client):
    index_records(elasticsearch_client, build_one_access_every_month_for_one_item())
    index_records(elasticsearch_client,
                  build_one_access_every_month_for_one_item(institution_id='udm'))
    return elasticsearch_client


@pytest.fixture
def alternate_controlled_and_oa_for_one_item_every_month(
        elasticsearch_client, one_controlled_access_for_one_item_every_month):
    index_records(elasticsearch_client, build_one_access_every_month_for_one_item(False))
    return elasticsearch_client


@pytest.fixture
def alternate_controlled_and_oa_for_one_item_and_one_invstigation_every_month(
        elasticsearch_client, alternate_controlled_and_oa_for_one_item_every_month):
    index_records(elasticsearch_client,
                  build_one_access_every_month_for_one_item(False, is_request=False))
    return elasticsearch_client


@pytest.fixture
def alternate_unique_and_not_for_one_item_every_month(elasticsearch_client):
    index_records(elasticsearch_client,
                  build_one_unique_access_one_not_unique_every_month_for_one_item())
    return elasticsearch_client


@pytest.fixture
def two_thousand_accesses(elasticsearch_client):
    index_records(elasticsearch_client, build_two_thousand_journals())
    return elasticsearch_client
