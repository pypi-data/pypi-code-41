from urllib import parse as urlparse

from django.core.paginator import EmptyPage, Paginator
from django.utils.encoding import force_str

from .exceptions import ImmediateResponseError


def paginate_queryset(queryset, url, pagination_data):
    """Given a queryset and pagination information, return the paginated queryset
    as well as the pagination metadata.

    :param django.Model queryset: The queryset that will be paginated
    :param URL url: A valid url
    :param Pagination pagination: Pagination params
    :return: A tuple containing the paginated query set and the pagination data
    :rtype (queryset, dict)
    """
    paginator = Paginator(queryset, pagination_data.page_size)

    try:
        page = paginator.page(pagination_data.page)
    except EmptyPage:
        from .responses import PaginationErrorResponse

        raise ImmediateResponseError(
            PaginationErrorResponse("That page does not exist")
        )

    return page.object_list, _create_pagination_metadata(page, url)


def _create_pagination_metadata(page, url):
    """Returns a dictionary that contains the pagination metadata
    as well as links to next and previous pages if they are available.

    :param paginator.Page page: The
    :param URL url: A request that knows how to build
     it's own absolute url.
    :return: The pagination dictionary
    :rtype dict
    """
    meta_params = [
        "limit",
        "total_objects",
        "num_pages",
        "page",
        "next_page",
        "previous_page",
    ]
    meta = {param: None for param in meta_params}

    if page is None or not url:
        return meta

    meta["page_size"] = page.paginator.per_page
    meta["page"] = page.number
    meta["next_page"] = _get_page_url(url, page.next_page_number)
    meta["previous_page"] = _get_page_url(url, page.previous_page_number)
    meta["total_objects"] = page.paginator.count

    try:
        meta["num_pages"] = page.paginator.num_pages
    except ZeroDivisionError:
        meta["num_pages"] = 1

    return meta


def _get_page_url(url, page_func):
    """Given a url and a paginator function, return the next/previous page or
    None if the page doesn't exist."""
    try:
        page_number = page_func()
    except (EmptyPage, ZeroDivisionError):
        return None
    return _replace_query_param(url, "page", page_number)


# From rest_framework
def _replace_query_param(url, key, val):
    """
    Given a URL and a key/val pair, set or replace an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(force_str(url))
    query_dict = urlparse.parse_qs(query, keep_blank_values=True)
    query_dict[force_str(key)] = [force_str(val)]
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))
