# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collective.edtf_behavior.behaviors.edtf_date import IEDTFDate
from collective.edtf_behavior.behaviors.edtf_date import IEDTFDateMarker
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer


@indexer(IDexterityContent)
def dummy(obj):
    """Dummy to prevent indexing child objects"""
    raise AttributeError('This field should not indexed here!')


@indexer(IEDTFDateMarker)
def date_latest(obj):
    adapted_obj = IEDTFDate(obj)
    return adapted_obj.date_latest


@indexer(IEDTFDateMarker)
def date_earliest(obj):
    adapted_obj = IEDTFDate(obj)
    return adapted_obj.date_earliest


@indexer(IEDTFDateMarker)
def date_sort_ascending(obj):
    adapted_obj = IEDTFDate(obj)
    return adapted_obj.date_sort_ascending


@indexer(IEDTFDateMarker)
def date_sort_descending(obj):
    adapted_obj = IEDTFDate(obj)
    return adapted_obj.date_sort_descending
