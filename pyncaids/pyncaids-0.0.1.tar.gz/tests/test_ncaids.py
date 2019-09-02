# -*- coding: utf-8 -*-

"""test_ncaids.py
   Copyright (c) 2019 Jacek Artymiak
   All Rights Reserved.
"""

# Python standard library imports

# Application imports

import pyncaids


######################
# NCA identifier tests


def test_nca_by_authority_id():
    nca = pyncaids.NCA()
    authority_list = nca.nca_by_authority_id("GB-FCA")

    # data assertions

    assert len(authority_list) == 1
    assert authority_list[0].get("authority_id") == "GB-FCA"
    assert authority_list[0].get("country") == "United Kingdom"
    assert authority_list[0].get("authority_name") == "Financial Conduct Authority"


def test_nca_by_partial_authority_id():
    nca_dict =  {
        "authority_id": "GB-FCA",
        "country": "United Kingdom",
        "authority_name": "Financial Conduct Authority"
    }
    nca = pyncaids.NCA()
    authority_list = nca.nca_by_partial_authority_id("A")

    # data assertions

    assert len(authority_list) > 1
    assert nca_dict in authority_list


def test_nca_by_country():
    nca = pyncaids.NCA()
    authority_list = nca.nca_by_country("United Kingdom")

    # data assertions

    assert len(authority_list) == 1
    assert authority_list[0].get("authority_id") == "GB-FCA"
    assert authority_list[0].get("country") == "United Kingdom"
    assert authority_list[0].get("authority_name") == "Financial Conduct Authority"


def test_nca_by_partial_country():
    nca_dict =  {
        "authority_id": "GB-FCA",
        "country": "United Kingdom",
        "authority_name": "Financial Conduct Authority"
    }
    nca = pyncaids.NCA()
    authority_list = nca.nca_by_partial_country("i")

    # data assertions

    assert len(authority_list) > 1
    assert nca_dict in authority_list


def test_nca_by_authority_name():
    nca = pyncaids.NCA()
    authority_list = nca.nca_by_authority_name("Financial Conduct Authority")

    # data assertions

    assert len(authority_list) == 1
    assert authority_list[0].get("authority_id") == "GB-FCA"
    assert authority_list[0].get("country") == "United Kingdom"
    assert authority_list[0].get("authority_name") == "Financial Conduct Authority"


def test_nca_by_partial_authority_name():
    nca_dict =  {
        "authority_id": "GB-FCA",
        "country": "United Kingdom",
        "authority_name": "Financial Conduct Authority"
    }
    nca = pyncaids.NCA()
    authority_list = nca.nca_by_partial_authority_name("Authority")

    # data assertions

    assert len(authority_list) > 1
    assert nca_dict in authority_list
