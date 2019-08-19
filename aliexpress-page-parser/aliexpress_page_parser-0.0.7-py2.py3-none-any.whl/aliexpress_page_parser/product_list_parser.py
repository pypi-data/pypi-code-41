# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import sys
import re
import json
import math
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

try:
    from HTMLParser import HTMLParser
except ImportError:
    if sys.version_info[0:2] >= (3, 4):
        from html import unescape
    else:
        from html.parser import HTMLParser

import dukpy
from parsel import Selector

from aliexpress_page_parser import logger


class ProductListParser(object):
    def __init__(self, text, type='html', namespaces=None, root=None, base_url=None):
        self.selector = Selector(
            text, type=type, namespaces=namespaces, root=root, base_url=base_url)

    def parse(self):
        result = {'products': []}

        next_page_url = self.parse_js_next_page_url()
        if next_page_url is None:
            next_page_elem = self.selector.xpath(
                '//div[@id="pagination-bottom"]/div[contains(@class, "ui-pagination-navi")]/a[contains(@class, "page-next")]')
            next_page_url = next_page_elem.xpath('./@href').extract_first()
            if next_page_url:
                if next_page_url.startswith('//'):
                    next_page_url = 'https:' + next_page_url

                result['next_page_url'] = next_page_url
        else:
            result['next_page_url'] = next_page_url

        grid_elems = self.selector.xpath('//ul[@id="hs-below-list-items"]/li')
        list_elems = self.selector.xpath('//ul[@id="hs-list-items"]/li')
        list_products_template = self.selector.xpath(
            '//div[@id="hs-below-list-items"]/script/text()').extract_first()
        if list_products_template:
            list_elems.extend(Selector(text=list_products_template).xpath('//ul/li'))

        for product_elem in grid_elems:
            try:
                result['products'].append(self.parse_grid_product(product_elem))
            except Exception as e:
                logger.exception(e)

        for product_elem in list_elems:
            try:
                result['products'].append(self.parse_list_product(product_elem))
            except Exception as e:
                logger.exception(e)

        result['products'].extend(self.parse_js_products())

        return result

    @classmethod
    def parse_json(cls, json_response):
        result = dict()

        if not isinstance(json_response, dict):
            try:
                json_response = unescape(json_response)
            except:
                html_parser = HTMLParser()
                json_response = html_parser.unescape(json_response)
            json_response = json.loads(json_response)

        result_count = json_response.get('resultCount', 0)
        result_size_per_page = json_response.get('resultSizePerPage', 60)
        pages = math.floor((result_count + result_size_per_page - 1) / result_size_per_page)

        d = dict()
        current_page = json_response.get('p4pObjectConfig', d).get('bcfg', d).get('pageIndex', 1)
        if current_page < pages:
            result['next_page'] = current_page + 1

        result['products'] = cls.format_products(json_response.get('items', []))

        return result

    def parse_js_next_page_url(self):
        scripts = ['var window = {}; var PAGE_TIMING = {}; var Image = Object;']
        for script_elem in self.selector.css('script'):
            script_content = script_elem.xpath('./text()').extract_first()
            if script_content and re.match(r'.*runConfigs', script_content, re.M | re.S):
                scripts.append(script_content)

        interpreter = dukpy.JSInterpreter()
        interpreter.evaljs(''.join(scripts))
        run_configs = interpreter.evaljs('window.runConfigs')

        if not run_configs:
            return None

        search_ajax_url = run_configs.get('searchAjaxUrl', None)
        if not search_ajax_url:
            return None

        search_query = run_configs.get('searchQuery', None)
        if not search_query:
            return None

        page_nav = run_configs.get('pageNav', None)
        if not page_nav:
            return None

        current_page = page_nav.get('currentPage', 1)
        max_page = page_nav.get('maxPage', 1)
        if max_page <= current_page:
            return None

        search_ajax_url = search_ajax_url.split('?').pop(0)
        if search_ajax_url.startswith('//'):
            search_ajax_url = 'https:' + search_ajax_url

        if 'SortType' not in search_query:
            search_query['SortType'] = 'default'

        search_query['page'] = current_page + 1
        search_text = search_query.get('SearchText', '')
        if hasattr(search_text, 'decode'):
            search_text = search_text.decode('utf-8', 'ignore')
        search_query['SearchText'] = search_text

        return u'{}?{}'.format(search_ajax_url, urlencode(search_query))

    def parse_js_products(self):
        scripts = ['var window = {}; var PAGE_TIMING = {}; var Image = Object;']
        for script_elem in self.selector.css('script'):
            script_content = script_elem.xpath('./text()').extract_first()
            if script_content and re.search(r'window.runParams', script_content):
                scripts.append(script_content)

        interpreter = dukpy.JSInterpreter()
        interpreter.evaljs(''.join(scripts))
        run_params = interpreter.evaljs('window.runParams')
        if not run_params:
            return []

        return self.format_products(run_params.get('items', []))

    @classmethod
    def format_products(self, product_items):
        products = []
        for item in product_items:
            try:
                price = float(item['price'].split('$').pop().strip().split('-').pop(0).strip())
            except:
                price = 0

            try:
                orders = int(item.get('tradeDesc', '').split().pop(0).strip())
            except:
                orders = 0

            products.append({
                'title': item['title'],
                'url': 'https:' + item['productDetailUrl'],
                'product_id': str(item['productId']),
                'price': price,
                'rating': float(item.get('starRating', 0)),
                'feedback': 0,
                'orders': orders
            })

        return products

    def parse_grid_product(self, product_elem):
        info_elem = product_elem.xpath('./div[@class="item"]/div[@class="info"]')
        if not info_elem:
            raise ValueError('Could not find product information!')

        title = info_elem.xpath('./h3/a/@title').extract_first()
        if not title:
            raise ValueError('Could not parse title.')

        url = info_elem.xpath('./h3/a/@href').extract_first()
        if url.startswith('//'):
            url = 'https:' + url

        matched = re.match(r".*www\.aliexpress\.com\/item\/.*\/([0-9]+)\.html\?.*", url)
        if matched and len(matched.groups()) > 0:
            product_id = matched.groups()[0]
        else:
            raise ValueError('Could not find product_id - %s' % url)

        try:
            price_str = info_elem.xpath(
                './span[contains(@class, "price")]/span[@itemprop="price"]/text()').extract_first()
            price = float(price_str.split('$').pop().strip().split('-').pop(0).strip())
        except:
            price = 0

        star_str = info_elem.xpath(
            './div[@class="rate-history"]/span[contains(@class, "star")]/@title').extract_first()
        if star_str:
            rating = float(star_str.split(':').pop().strip().split().pop(0))
        else:
            rating = 0

        feedback_str = info_elem.xpath(
            './div[@class="rate-history"]/a[contains(@class, "rate-num")]/@title').extract_first()
        if feedback_str:
            matched = re.match(r"Feedback\((.+)\)", feedback_str)
            if matched:
                feedbacks = int(matched.group(1))
            else:
                feedbacks = 0
        else:
            feedbacks = 0

        orders_str = info_elem.xpath(
            './div[@class="rate-history"]/span[contains(@class, "order-num")]/a/em/text()').extract_first()
        if orders_str:
            try:
                orders = int(
                    orders_str.strip().split(' ').pop().replace('(', '').replace(')', ''))
            except:
                orders = 0
        else:
            orders = 0

        return {
            'product_id': product_id,
            'title': title,
            'url': url,
            'price': price,
            'rating': rating,
            'feedback': feedbacks,
            'orders': orders
        }

    def parse_list_product(self, product_elem):
        detail_elem = product_elem.xpath('.//div[contains(@class, "detail")]/h3/a')

        title = detail_elem.xpath('./@title').extract_first().strip()
        if not title:
            raise ValueError('Could not parse title.')

        url = detail_elem.xpath('./@href').extract_first()
        if url.startswith('//'):
            url = 'https:' + url

        matched = re.match(r".*www\.aliexpress\.com\/item\/.*\/([0-9]+)\.html\?.*", url)
        if matched and len(matched.groups()) > 0:
            product_id = matched.groups()[0]
        else:
            raise ValueError('Could not find product_id - %s' % url)

        info_elem = product_elem.xpath('.//div[contains(@class, "infoprice")]')
        try:
            price_str = info_elem.xpath(
                './span[contains(@class, "price")]/span[@itemprop="price"]/text()').extract_first()
            price = float(price_str.split('$').pop().strip().split('-').pop(0).strip())
        except:
            price = 0

        star_str = info_elem.xpath(
            './div[@class="rate-history"]/span[contains(@class, "star")]/@title').extract_first()
        if star_str:
            try:
                rating = float(star_str.split(':').pop().strip().split().pop(0))
            except:
                rating = 0
        else:
            rating = 0

        feedback_str = info_elem.xpath(
            './div[@class="rate-history"]/a[contains(@class, "rate-num")]/text()').extract_first()
        if feedback_str:
            matched = re.match(r"Feedback\((.+)\)", feedback_str)
            if matched:
                feedbacks = int(matched.group(1))
            else:
                feedbacks = 0
        else:
            feedbacks = 0

        orders_str = info_elem.xpath(
            './div[@class="rate-history"]/span[contains(@class, "order-num")]/a/em/text()').extract_first()
        if orders_str:
            try:
                orders = int(
                    orders_str.strip().split(' ').pop().replace('(', '').replace(')', ''))
            except:
                orders = 0
        else:
            orders = 0

        return {
            'product_id': product_id,
            'title': title,
            'url': url,
            'price': price,
            'rating': rating,
            'feedback': feedbacks,
            'orders': orders
        }
