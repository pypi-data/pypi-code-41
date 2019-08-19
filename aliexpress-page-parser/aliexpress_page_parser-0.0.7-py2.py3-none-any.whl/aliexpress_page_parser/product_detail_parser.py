# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import re
import dukpy

from parsel import Selector

from aliexpress_page_parser import logger


class ProductDetailParser(object):
    def __init__(self, text, type='html', namespaces=None, root=None, base_url=None):
        self.selector = Selector(
            text, type=type, namespaces=namespaces, root=root, base_url=base_url)

    def parse(self):
        product = dict()
        d = dict()

        scripts = ['var window = {}; var PAGE_TIMING = {}; var Image = Object;']
        for script_elem in self.selector.css('script'):
            script_content = script_elem.xpath('./text()').extract_first()
            if script_content and re.match(r'.*runParams', script_content, re.M | re.S):
                scripts.append(script_content)

        interpreter = dukpy.JSInterpreter()
        interpreter.evaljs(''.join(scripts))
        run_params = interpreter.evaljs('window.runParams')
        run_params = run_params.get('data', d)

        page_module = run_params.get('pageModule', d)
        product['meta_keywords'] =  page_module.get('keywords', '')
        product['meta_description'] = page_module.get('description', '')
        product['product_id'] = str(page_module.get('productId', ''))

        breadcrumbs = []
        for bcp in run_params.get('crossLinkModule', d).get('breadCrumbPathList', []):
            name = bcp.get('name', '')
            if not name:
                continue

            url = bcp.get('url', '')
            if not url.startswith('https://www.aliexpress.com/category'):
                continue

            matched = re.match(r'.*category/([0-9]+)/.*', url)
            if not matched:
                continue
            cid = matched.groups()[0]

            breadcrumbs.append({'name': name, 'url': url, 'cid': cid})
        product['breadcrumbs'] = breadcrumbs

        title_module = run_params.get('titleModule', d)

        product['title'] = title_module.get('subject', '')
        product['rating'] = float(title_module.get('feedbackRating', d).get('averageStar', 0))
        product['feedback'] = int(title_module.get('feedbackRating', d).get('totalValidNum', 0))
        product['orders'] = int(title_module.get('formatTradeCount', 0))

        specs = []
        for prop in run_params.get('specsModule', d).get('props', []):
            name = prop.get('attrName', '')
            value = prop.get('attrValue', '')
            if name and value:
                spec = dict()
                spec[name] = value
                specs.append(spec)
        product['specs'] = specs

        # TODO: packaging
        product['gallery_images'] = list(run_params.get('imageModule', d).get('imagePathList', []))

        sku_module = run_params.get('skuModule', d)

        options = []
        for sku_property in sku_module.get('productSKUPropertyList', []):
            option = {
                'id': str(sku_property.get('skuPropertyId', '')),
                'name': sku_property.get('skuPropertyName', ''),
                'skus': []
            }

            for property_value in sku_property.get('skuPropertyValues', []):
                option['skus'].append({
                    'id': str(property_value.get('propertyValueId', '')),
                    'name': property_value.get('propertyValueDisplayName', ''),
                    'img_url': property_value.get('skuPropertyImagePath', '')
                })

            options.append(option)
        product['options'] = options

        product['sku_products'] = sku_module.get('skuPriceList', [])

        store_module = run_params.get('storeModule', d)
        product['store'] = {
            'id': str(store_module.get('storeNum', '')),
            'name': store_module.get('storeName', ''),
            'url': 'https:' + store_module.get('storeURL', ''),
            'top_rated': store_module.get('topRatedSeller', False),
            'open_date': store_module.get('openTime', ''),
            'location': store_module.get('countryCompleteName', ''),
            'followings': store_module.get('followingNumber', 0),
            'positives': store_module.get('positiveNum', 0),
            'positive_rate': float(store_module.get('positiveRate', '0%').strip('%')),
        }

        freight_module = run_params.get('freightItemModule', d)
        product['freight'] = {
            'company': freight_module.get('company', ''),
            'currency': freight_module.get('freightAmount', d).get('currency', ''),
            'amount': freight_module.get('freightAmount', d).get('value', 0),
            'time': freight_module.get('time', ''),
            'tracking': freight_module.get('tracking', False),
            'service_name': freight_module.get('serviceName', ''),
            'send_goods_country': freight_module.get('sendGoodsCountry', '')
        }

        return product
