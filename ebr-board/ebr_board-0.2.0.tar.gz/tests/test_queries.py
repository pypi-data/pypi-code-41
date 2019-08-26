#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_board` package."""

import pytest
from unittest.mock import patch

from ebr_board.database.queries import make_query


@patch("ebr_board.database.queries.BuildResults")
def test_make_query(mock_build_results):
    """
    Basic smoke test for make_query
    """
    result = make_query("test_index", None, [], [], agg=None, size=1, start=0)

    assert mock_build_results.search.called_with("test_index")
    assert mock_build_results.search.source.called_with([], [])
    assert mock_build_results.search.query.called_with("bool", filter=[None])
    assert mock_build_results.search.execute.called_with()


@patch("ebr_board.database.queries.BuildResults")
def test_make_query_agg(mock_build_results):
    """
    Basic smoke test for make_query with aggregation
    """
    result = make_query("test_index", None, [], [], agg="agg", size=1, start=0)

    assert mock_build_results.search.called_with("test_index")
    assert mock_build_results.search.source.called_with([], [])
    assert mock_build_results.search.aggs.metric.called_with("fail_count", "agg")
    assert mock_build_results.search.query.called_with("bool", filter=[None])
    assert mock_build_results.search.execute.called_with()
