# -*- coding: utf-8 -*-

# Copyright :copyright: 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

import os
import io
import glob

import pytest


@pytest.fixture(scope='session')
def pages_dir():
    return os.path.join(os.path.dirname(__file__), 'pages')

@pytest.fixture(scope='session')
def product_grid_page_source(pages_dir):
    product_grid_file_path = os.path.join(pages_dir, 'products_grid.html')
    with io.open(product_grid_file_path, 'rb') as fh:
        content = fh.read().decode('utf-8', 'ignore')

    return content

@pytest.fixture(scope='session')
def product_list_page_source(pages_dir):
    product_list_file_path = os.path.join(pages_dir, 'products_list.html')
    with io.open(product_list_file_path, 'rb') as fh:
        content = fh.read().decode('utf-8', 'ignore')

    return content

@pytest.fixture(scope='session')
def product_search_result_page_sources(pages_dir):
    sources = dict()

    product_search_result_pathes = glob.glob('{}/products_search_result*.html'.format(pages_dir))
    for search_result_path in product_search_result_pathes:
        file_name, _ = os.path.splitext(os.path.basename(search_result_path))
        search_result_key = file_name.split('_').pop()
        with io.open(search_result_path, 'rb') as fh:
            sources[search_result_key] = fh.read().decode('utf-8', 'ignore')

    return sources

@pytest.fixture(scope='session')
def product_search_json_result(pages_dir):
    with io.open(os.path.join(pages_dir, 'search_result.html'), 'rb') as fh:
        content = fh.read().decode('utf-8', 'ignore')

    return content

@pytest.fixture(scope='session')
def product_detail_page_sources(pages_dir):
    sources = []

    product_detail_file_pathes = glob.glob('{}/product_detail_*.html'.format(pages_dir))
    for file_path in product_detail_file_pathes:
        with io.open(file_path, 'rb') as fh:
            sources.append(fh.read().decode('utf-8'))

    return sources

@pytest.fixture(scope='session')
def target_json_search_result():
    return {
        'next_page': 3,
        'products': [
            {
                'title': 'Tape Patches Forehead Stickers Skin-Lift-Up Anti-Wrinkle Frown Smile-Lines',
                'url': 'https://www.aliexpress.com/item/Forehead-Stickers-anti-Wrinkle-Skin-Lift-Up-Tape-Frown-Smile-Lines-Forehead-Anti-Wrinkle-Patches/33056159299.html?algo_pvid=2d9c80ec-39a8-4e62-aeab-5bfbdea2aefd&algo_expid=2d9c80ec-39a8-4e62-aeab-5bfbdea2aefd-0&btsid=1bd9f623-67fe-4b20-8201-cfe243942bc8&ws_ab_test=searchweb0_0,searchweb201602_4,searchweb201603_52',
                'product_id': '33056159299',
                'price': 4.73,
                'rating': 0,
                'feedback': 0,
                'orders': 0
            },
            {
                'title': 'Skin-Care-Tools Eye-Massager Vibrating Remover Frown-Lines Face Anti-Wrinkle Micro-Current',
                'url': 'https://www.aliexpress.com/item/Micro-current-Eye-Wand-Vibrating-Eye-Massager-Negative-Ion-Importing-Frown-Lines-Remover-Anti-Wrinkle-Eyes/4000064271777.html?algo_pvid=2d9c80ec-39a8-4e62-aeab-5bfbdea2aefd&algo_expid=2d9c80ec-39a8-4e62-aeab-5bfbdea2aefd-3&btsid=1bd9f623-67fe-4b20-8201-cfe243942bc8&ws_ab_test=searchweb0_0,searchweb201602_4,searchweb201603_52',
                'product_id': '4000064271777',
                'price': 3.12,
                'rating': 0,
                'feedback': 0,
                'orders': 0
            },
            {
                'title': "I'm Sarcastic Because Punching People Is Frowned Sarcasm Novelty Funny T Shirt",
                'url': 'https://www.aliexpress.com/item/I-m-Sarcastic-Because-Punching-People-Is-Frowned-Sarcasm-Novelty-Funny-T-Shirt/32998436696.html?algo_pvid=2d9c80ec-39a8-4e62-aeab-5bfbdea2aefd&algo_expid=2d9c80ec-39a8-4e62-aeab-5bfbdea2aefd-59&btsid=1bd9f623-67fe-4b20-8201-cfe243942bc8&ws_ab_test=searchweb0_0,searchweb201602_4,searchweb201603_52',
                'product_id': '32998436696',
                'price': 11.04,
                'rating': 0,
                'feedback': 0,
                'orders': 0
            },
        ]
    }

@pytest.fixture(scope='session')
def target_search_results():
    return {
        '1': {
            'next_page_url': 'https://www.aliexpress.com/glosearch/api/product?ltype=wholesale&d=y&CatId=0&SearchText=nembutal&trafficChannel=main&SortType=default&page=2',
            'products': [
                {
                    'title': 'Brooch Badge Suicide Silence-Pins Depression Prevention Mental Health Emotional-Jew Awareness',
                    'url': 'https://www.aliexpress.com/item/It-is-ok-not-to-be-ok-pin-mental-health-awareness-badge-depression-suicide-prevention-brooch/32968630915.html?algo_pvid=6df71766-a829-4deb-9933-384bfadb1db9&algo_expid=6df71766-a829-4deb-9933-384bfadb1db9-0&btsid=3af5ce90-a0bd-453b-8ece-76d8c1a24265&ws_ab_test=searchweb0_0,searchweb201602_5,searchweb201603_60',
                    'product_id': '32968630915',
                    'price': 2.81,
                    'rating': 5.0,
                    'feedback': 0,
                    'orders': 147
                },
                {
                    'title': 'Power-Knob Spinner Boat-Handle Steering-Wheel Marine Heavy-Duty Stainless-Steel Car Truck',
                    'url': 'https://www.aliexpress.com/item/Universal-Stainless-Steel-Steering-Wheel-Spinner-Heavy-Duty-Car-Truck-Marine-Boat-Handle-Suicide-Power-Knob/32779454090.html?algo_pvid=6df71766-a829-4deb-9933-384bfadb1db9&algo_expid=6df71766-a829-4deb-9933-384bfadb1db9-11&btsid=3af5ce90-a0bd-453b-8ece-76d8c1a24265&ws_ab_test=searchweb0_0,searchweb201602_5,searchweb201603_60',
                    'product_id': '32779454090',
                    'price': 11.88,
                    'rating': 4.7,
                    'feedback': 0,
                    'orders': 137
                },
                {
                    'title': 'Retro Poster Painting Joker Suicide Squad Quinn Good-Printed Harley Home-Decor Vintage',
                    'url': 'https://www.aliexpress.com/item/Suicide-Squad-Retro-Poster-Harley-Quinn-and-The-Joker-Good-Printed-Art-Poster-Vintage-Kraft-Paper/32955732729.html?algo_pvid=6df71766-a829-4deb-9933-384bfadb1db9&algo_expid=6df71766-a829-4deb-9933-384bfadb1db9-59&btsid=3af5ce90-a0bd-453b-8ece-76d8c1a24265&ws_ab_test=searchweb0_0,searchweb201602_5,searchweb201603_60',
                    'product_id': '32955732729',
                    'price': 1.81,
                    'rating': 4.8,
                    'feedback': 0,
                    'orders': 86
                },
            ]
        }
    }

@pytest.fixture(scope='session')
def target_grid_products_result():
    return {
        'next_page_url': 'https://www.aliexpress.com/wholesale?initiative_id=SB_20190628131348&site=glo&g=y&SearchText=toy+train&page=2',
        'products': [
            {
                'title': 'EDWONE Wood Magnetic Train Plane Wood Railway Helicopter Car Truck Accessories Toy For Kids Fit Wood new Biro Tracks Gifts',
                'url': 'https://www.aliexpress.com/item/EDWONE-Wood-Magnetic-Train-Plane-Wood-Railway-Helicopter-Car-Truck-Accessories-Toy-For-Kids-Fit-Wood/32960792757.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=89536c81-fc05-476a-bc06-bb032fbe68ea-0&algo_pvid=89536c81-fc05-476a-bc06-bb032fbe68ea',
                'product_id': '32960792757',
                'price': 1.82,
                'rating': 4.9,
                'feedback': 1167,
                'orders': 1335
            },
            {
                'title': 'New Emily Wood Train Magnetic Wooden Trains Car Toy Model Magnetic Toys Christmas Gift Kids Children Fit Wooden Thomas Tracks',
                'url': 'https://www.aliexpress.com/item/New-Emily-Wood-Train-Magnetic-Wooden-Trains-Car-Toy-Model-Magnetic-Toys-Christmas-Gift-Kids-Children/32984870526.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=89536c81-fc05-476a-bc06-bb032fbe68ea-1&algo_pvid=89536c81-fc05-476a-bc06-bb032fbe68ea',
                'product_id': '32984870526',
                'price': 1.84,
                'rating': 4.9,
                'feedback': 427,
                'orders': 619
            },
            {
                'title': 'Plastic Grey Double Tunnel Wooden Train Track Accessories Tunnel Track Train Slot Wood Railway Toys bloques de construccion',
                'url': 'https://www.aliexpress.com/item/Plastic-Grey-Double-Tunnel-Wooden-Train-Track-Accessories-Tunnel-Track-Train-Slot-Wood-Railway-Toys-bloques/33024845839.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=89536c81-fc05-476a-bc06-bb032fbe68ea-46&algo_pvid=89536c81-fc05-476a-bc06-bb032fbe68ea',
                'product_id': '33024845839',
                'price': 8.78,
                'rating': 0,
                'feedback': 0,
                'orders': 10
            },
            {
                'title': "The Children's Birthday Gift Thomas Small Locomotive Installed Electric Rail Racing Simulation Toy Boy Toy Electric Train Track",
                'url': 'https://www.aliexpress.com/item/The-Children-s-Birthday-Gift-Thomas-Small-Locomotive-Installed-Electric-Rail-Racing-Simulation-Toy-Boy-Toy/32944868569.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=89536c81-fc05-476a-bc06-bb032fbe68ea-47&algo_pvid=89536c81-fc05-476a-bc06-bb032fbe68ea',
                'product_id': '32944868569',
                'price': 10.29,
                'rating': 4.6,
                'feedback': 8,
                'orders': 24
            }
        ]
    }

@pytest.fixture(scope='session')
def target_list_products_result():
    return {
        'next_page_url': 'https://www.aliexpress.com/wholesale?initiative_id=SB_20190628142929&site=glo&SearchText=cups&needQuery=n&page=2',
        'products': [
            {
                'title': '270ML Travel Cup Stainless Steel Silicone Retractable Folding cups Telescopic Collapsible Coffee Cups Outdoor Sport Water Cup',
                'url': 'https://www.aliexpress.com/item/270ML-Travel-Cup-Stainless-Steel-Silicone-Retractable-Folding-cups-Telescopic-Collapsible-Coffee-Cups-Outdoor-Sport-Water/32888842394.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c-0&algo_pvid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c',
                'product_id': '32888842394',
                'price': 2.86,
                'rating': 4.9,
                'feedback': 1158,
                'orders': 1837
            },
            {
                'title': 'Hot New Folding Silicone Portable Silicone Telescopic Drinking Collapsible coffee cup multi-function folding silica cup Travel',
                'url': 'https://www.aliexpress.com/item/Hot-New-Folding-Silicone-Portable-Silicone-Telescopic-Drinking-Collapsible-coffee-cup-multi-function-folding-silica-cup/32978513055.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c-1&algo_pvid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c',
                'product_id': '32978513055',
                'price': 5.79,
                'rating': 4.9,
                'feedback': 340,
                'orders': 812
            },
            {
                'title': '2019 New Trend Ceramics Hand-painted Retro Creative Coffee Cup Coffee Bar Relief Personality Breakfast Milk Cup Exquisite Gifts',
                'url': 'https://www.aliexpress.com/item/2019-New-Trend-Ceramics-Hand-painted-Retro-Creative-Coffee-Cup-Coffee-Bar-Relief-Personality-Breakfast-Milk/32974346726.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c-46&algo_pvid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c',
                'product_id': '32974346726',
                'price': 11.48,
                'rating': 4.9,
                'feedback': 53,
                'orders': 72
            },
            {
                'title': '320ml Kids Baby Feeding Bottle Cute Rabbit Style Thermos Cup Stainless Steel Keep Water Hot Suitable For Kids Child School',
                'url': 'https://www.aliexpress.com/item/320ml-Kids-Baby-Feeding-Bottle-Cute-Rabbit-Style-Thermos-Cup-Stainless-Steel-Keep-Water-Hot-Suitable/32961200402.html?ws_ab_test=searchweb0_0,searchweb201602_5_10065_10130_10068_10547_319_10546_317_10548_10545_10696_10084_453_454_10083_10618_10307_537_536_10059_10884_10887_321_322_10103,searchweb201603_52,ppcSwitch_0&algo_expid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c-47&algo_pvid=bcd3f362-c9e0-4f07-8eb5-d8133cf0268c',
                'product_id': '32961200402',
                'price': 10.36,
                'rating': 4.9,
                'feedback': 26,
                'orders': 106
            }
        ]
    }

@pytest.fixture(scope='session')
def target_product_details():
    return {
        '33012575485': {
            'product_id': '33012575485',
            'meta_keywords': "Women's Watches, Cheap Women's Watches, NAVIFORCE New Women Luxury Brand Watch Simple Quartz Lady Waterproof Wristwatch Female Fashion Casual Watches Clock reloj mujer",
            'meta_description': u"Cheap Women's Watches, Buy Directly from China Suppliers:NAVIFORCE New Women Luxury Brand Watch Simple Quartz Lady Waterproof Wristwatch Female Fashion Casual Watches Clock reloj mujer\nEnjoy ✓Free Shipping Worldwide! ✓Limited Time Sale ✓Easy Return.",
            'title': 'NAVIFORCE New Women Luxury Brand Watch Simple Quartz Lady Waterproof Wristwatch Female Fashion Casual Watches Clock reloj mujer',
            'rating': 4.8,
            'feedback': 36,
            'orders': 558,
            'breadcrumbs': [
                {
                    'name': 'Watches',
                    'url': 'https://www.aliexpress.com/category/1511/watches.html',
                    'cid': '1511'
                },
                {
                    'name': "Women's Watches",
                    'url': 'https://www.aliexpress.com/category/200214036/women-watches.html',
                    'cid': '200214036'
                }
            ],
            'specs': [
                {'Movement': 'Quartz'},
                {'Case Material': 'Stainless Steel'},
                {'Clasp Type': 'Buckle'},
                {'Water Resistance Depth': '3Bar'},
                {'Style': 'Fashion & Casual'},
                {'Feature': 'Auto Date,Complete Calendar,Shock Resistant,Water Resistant'},
                {'Model Number': 'NF-5005'},
                {'Band Material Type': 'Leather'},
                {'Band Width': '20'},
                {'Band Length': '22'},
                {'Case Thickness': '8'},
                {'Dial Diameter': '32'},
                {'Boxes & Cases Material': 'Paper'},
                {'Dial Window Material Type': 'Hardlex'},
                {'Case Shape': 'Round'},
                {'Brand Name': 'NAVIFORCE'},
                {'Women Watch': 'Women Wristwatches'},
                {'Relogio Masculino': 'Quartz Watch Brand Women'},
                {'Fashion Casual Watch': 'Watches For Women'},
                {'Quartz-Watch Women': 'Sport Watches'},
                {'Naviforce Watch Women': 'Women Quartz-Watch'},
                {'Quartz Wristwatches': 'Women Watches Top Brand Luxury'},
                {'Support': 'drop shipping watches'}
            ],
            'gallery_images': [
                "https://ae01.alicdn.com/kf/HTB1QJhCTSzqK1RjSZPxq6A4tVXaZ/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg",
                "https://ae01.alicdn.com/kf/HTB19mxKTMHqK1RjSZFPq6AwapXa2/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg",
                "https://ae01.alicdn.com/kf/HTB1KaFATPDpK1RjSZFrq6y78VXad/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg",
                "https://ae01.alicdn.com/kf/HTB1kX0STMHqK1RjSZFkq6x.WFXas/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg",
                "https://ae01.alicdn.com/kf/HTB1n8p_TNjaK1RjSZKzq6xVwXXay/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg",
                "https://ae01.alicdn.com/kf/HTB1vbFITOrpK1RjSZFhq6xSdXXaO/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg"
            ],
            'options': [
                {
                    'id': '14',
                    'name': 'Color',
                    'skus': [
                        {
                            'id': '201447598',
                            'name': 'gold',
                            'img_url': 'https://ae01.alicdn.com/kf/HTB1_chITNTpK1RjSZFKq6y2wXXaP/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg_640x640.jpg'
                        },
                        {
                            'id': '201447303',
                            'name': 'blue',
                            'img_url': 'https://ae01.alicdn.com/kf/HTB1FAtGTRLoK1RjSZFuq6xn0XXam/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg_640x640.jpg'
                        },
                        {
                            'id': '200005100',
                            'name': 'purple',
                            'img_url': 'https://ae01.alicdn.com/kf/HTB1DeVATMTqK1RjSZPhq6xfOFXar/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg_640x640.jpg'
                        },
                        {
                            'id': '200000080',
                            'name': 'sliver',
                            'img_url': 'https://ae01.alicdn.com/kf/HTB1rQVNTQPoK1RjSZKbq6x1IXXa9/NAVIFORCE-New-Women-Luxury-Brand-Watch-Simple-Quartz-Lady-Waterproof-Wristwatch-Female-Fashion-Casual-Watches-Clock.jpg_640x640.jpg'
                        }
                    ]
                }
            ],
            'sku_products': [
                {
                    "skuAttr": "14:201447303#blue",
                    "skuId": 67092454342,
                    "skuPropIds": "201447303",
                    "skuVal": {
                        "actSkuBulkCalPrice": "14.89",
                        "actSkuCalPrice": "15.19",
                        "actSkuDisplayBulkPrice": "US $14.89",
                        "actSkuMultiCurrencyBulkPrice": "14.89",
                        "actSkuMultiCurrencyCalPrice": "15.19",
                        "actSkuMultiCurrencyDisplayPrice": "15.19",
                        "availQuantity": 90,
                        "bulkOrder": 5,
                        "inventory": 100,
                        "isActivity": True,
                        "optionalWarrantyPrice": [
                        ],
                        "skuActivityAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $15.19",
                            "value": 15.19
                        },
                        "skuAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $189.90",
                            "value": 189.9
                        },
                        "skuBulkCalPrice": "186.1",
                        "skuCalPrice": "189.90",
                        "skuDisplayBulkPrice": "US $186.10",
                        "skuMultiCurrencyBulkPrice": "186.10",
                        "skuMultiCurrencyCalPrice": "189.9",
                        "skuMultiCurrencyDisplayPrice": "189.90"
                    }
                },
                {
                    "skuAttr": "14:201447598#gold",
                    "skuId": 67092454341,
                    "skuPropIds": "201447598",
                    "skuVal": {
                        "actSkuBulkCalPrice": "14.89",
                        "actSkuCalPrice": "15.19",
                        "actSkuDisplayBulkPrice": "US $14.89",
                        "actSkuMultiCurrencyBulkPrice": "14.89",
                        "actSkuMultiCurrencyCalPrice": "15.19",
                        "actSkuMultiCurrencyDisplayPrice": "15.19",
                        "availQuantity": 151,
                        "bulkOrder": 5,
                        "inventory": 200,
                        "isActivity": True,
                        "optionalWarrantyPrice": [
                          
                        ],
                        "skuActivityAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $15.19",
                            "value": 15.19
                        },
                        "skuAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $189.90",
                            "value": 189.9
                        },
                        "skuBulkCalPrice": "186.1",
                        "skuCalPrice": "189.90",
                        "skuDisplayBulkPrice": "US $186.10",
                        "skuMultiCurrencyBulkPrice": "186.10",
                        "skuMultiCurrencyCalPrice": "189.9",
                        "skuMultiCurrencyDisplayPrice": "189.90"
                    }
                },
                {
                    "skuAttr": "14:200005100#purple",
                    "skuId": 67092454343,
                    "skuPropIds": "200005100",
                    "skuVal": {
                        "actSkuBulkCalPrice": "14.89",
                        "actSkuCalPrice": "15.19",
                        "actSkuDisplayBulkPrice": "US $14.89",
                        "actSkuMultiCurrencyBulkPrice": "14.89",
                        "actSkuMultiCurrencyCalPrice": "15.19",
                        "actSkuMultiCurrencyDisplayPrice": "15.19",
                        "availQuantity": 90,
                        "bulkOrder": 5,
                        "inventory": 100,
                        "isActivity": True,
                        "optionalWarrantyPrice": [
                        ],
                        "skuActivityAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $15.19",
                            "value": 15.19
                        },
                        "skuAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $189.90",
                            "value": 189.9
                        },
                        "skuBulkCalPrice": "186.1",
                        "skuCalPrice": "189.90",
                        "skuDisplayBulkPrice": "US $186.10",
                        "skuMultiCurrencyBulkPrice": "186.10",
                        "skuMultiCurrencyCalPrice": "189.9",
                        "skuMultiCurrencyDisplayPrice": "189.90"
                    }
                },
                {
                    "skuAttr": "14:200000080#sliver",
                    "skuId": 67092454344,
                    "skuPropIds": "200000080",
                    "skuVal": {
                        "actSkuBulkCalPrice": "12.54",
                        "actSkuCalPrice": "12.79",
                        "actSkuDisplayBulkPrice": "US $12.54",
                        "actSkuMultiCurrencyBulkPrice": "12.54",
                        "actSkuMultiCurrencyCalPrice": "12.79",
                        "actSkuMultiCurrencyDisplayPrice": "12.79",
                        "availQuantity": 47,
                        "bulkOrder": 5,
                        "inventory": 100,
                        "isActivity": True,
                        "optionalWarrantyPrice": [
                        ],
                        "skuActivityAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $12.79",
                            "value": 12.79
                        },
                        "skuAmount": {
                            "currency": "USD",
                            "formatedAmount": "US $159.90",
                            "value": 159.9
                        },
                        "skuBulkCalPrice": "156.7",
                        "skuCalPrice": "159.90",
                        "skuDisplayBulkPrice": "US $156.70",
                        "skuMultiCurrencyBulkPrice": "156.70",
                        "skuMultiCurrencyCalPrice": "159.9",
                        "skuMultiCurrencyDisplayPrice": "159.90"
                    }
                }
            ],
            'store': {
                'id': '4683026',
                'name': 'NAVIFORCE Dropshipping Store',
                'url': 'https://www.aliexpress.com/store/4683026',
                'top_rated': False,
                'open_date': 'Jan 3, 2019',
                'location': 'China',
                'followings': 4826,
                'positives': 856,
                'positive_rate': 99.1,
            },
            'freight': {
                'company': 'AliExpress Standard Shipping',
                'currency': 'USD',
                'amount': 0,
                'time': '25-25',
                'tracking': True,
                'service_name': 'CAINIAO_STANDARD',
                'send_goods_country': 'CN'
            }
        }
    }
