# -*- coding: utf-8 -*-

from django.db.models.query import QuerySet


def pagination(queryset, page, num=10, strict=False, keeptype=False):
    """ Simple Pagination """
    page, num = int(page), int(num)
    start, stop = num * (page - 1), num * page
    if not keeptype:
        querylist = list(queryset[start: stop + 1])
        return querylist[start: stop], len(querylist[stop: stop + 1])
    return queryset[start: stop], max(queryset.count() if isinstance(queryset, QuerySet) else len(queryset) - stop, 0) if strict else len(queryset[stop: stop + 1])
