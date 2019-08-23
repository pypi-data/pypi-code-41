"""
Query functions to run against ElasticSearch
"""
# pylint: disable=invalid-name
from ebr_connector.schema.build_results import BuildResults

detailed_build_info = {
    "includes": [
        "br_build_date_time",
        "br_job_name",
        "br_job_url_key",
        "br_source",
        "br_build_id_key",
        "br_platform",
        "br_product",
        "br_status_key",
        "br_version_key",
        "br_tests_object",
    ],
    "excludes": [
        "lhi*",
        "br_tests_object.br_tests_passed_object.*",
        "br_tests_object.br_tests_failed_object.*",
        "br_tests_object.br_tests_skipped_object.*",
        "br_tests_object.br_suites_object.*",
    ],
}


def make_query(  # pylint: disable=too-many-arguments
    index, combined_filter, includes, excludes, agg=None, size=1, start=0
):
    """
    Simplifies the execution and usage of a typical query, including cleaning up the results.

    Args:
        index: index to search on
        combined_filter: combined set of filters to run the query with
        includes: list of fields to include on the results (keep as  small as possible to improve execution time)
        excludes: list of fields to explicitly exclude from the results
        size: [Optional] number of results to return. Defaults to 1.
    Returns:
        List of dicts with results of the query.
    """
    search = BuildResults().search(index=index)
    search = search.source(includes=includes, excludes=excludes)
    if agg:
        search = search.aggs.metric("fail_count", agg)
    search = search.query("bool", filter=[combined_filter])[0:1]
    search = search[start : start + size]
    response = search.execute()
    results = []

    if agg:
        results = response["aggregations"]["fail_count"]["buckets"]
    else:
        for hit in response["hits"]["hits"]:
            results.append(hit["_source"])
    return results
