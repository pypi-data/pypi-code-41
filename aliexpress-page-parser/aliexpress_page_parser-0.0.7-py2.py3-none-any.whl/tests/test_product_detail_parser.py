# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from aliexpress_page_parser.product_detail_parser import ProductDetailParser

import pytest

def test_parse(product_detail_page_sources, target_product_details):
    products = []
    for page_source in product_detail_page_sources:
        parser = ProductDetailParser(page_source)
        products.append(parser.parse())

    for product in products:
        target_product = target_product_details.get(product['product_id'])
        assert product == target_product
