#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.models.sales import *
from trivoreid.models.page import Page
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class SalesService(object):
    '''
    Class to wrap Trivore ID /sales APIs.
    '''
    _CATALOGS = 'api/rest/v1/sales/catalog'
    _CATALOG = 'api/rest/v1/sales/catalog/{}'
    _PRICING_PLANS = 'api/rest/v1/sales/pricingplan'
    _PRICING_PLAN = 'api/rest/v1/sales/pricingplan/{}'
    _PRODUCTS = 'api/rest/v1/sales/product'
    _PRODUCT = 'api/rest/v1/sales/product/{}'

    def __init__(self, credentials):
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._auth_header = credentials.access_token

    def get_all_catalogs(self,
                         filter_fields=None,
                         start_index=0,
                         count=100,
                         mergeProductDetails=False,
                         sortBy=None,
                         ascending=None):
        '''Get list of Paycards of the .
        Args:
            filter_fields (Filter)     : filter out the result.
            start_index (int)          : 0-based pagination start index
            count (int)                : pagination page size, max 500
            sortBy (str)               : sort by attribute name
            ascending (bool)           : if sort direction is ascending
            mergeProductDetails (bool) : copy missing values from original
                                         products to catalog items
        Returns:
            Page with the pagination data and the list of catalogs.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)

        params['mergeProductDetails'] = mergeProductDetails
        if sortBy != None:
            params['sortBy'] = sortBy
        if ascending != None:
            if ascending:
                params['sortOrder'] = 'ascending'
            else:
                params['sortOrder'] = 'descending'

        response = self._session.get(
                        su.uri(self._server, self._CATALOGS),
                        params=params,
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} catalogs'.format(len(response.json()['resources'])))
            catalogs = []
            for catalog in response.json()['resources']:
                catalogs.append(Catalog(catalog))
            return Page(response.json(), catalogs)
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_catalog(self, catalog):
        '''Create new Catalog for the .
        Args:
            catalog (Catalog)   : catalog to create
        Returns:
            New catalog object.
        Raises:
            TrivoreIDSDKException if the type of the Catalog is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Catalog' not in str(type(catalog)):
            raise TrivoreIDSDKException('Catalog type is wrong')

        response = self._session.post(
                        su.uri(self._server, self._CATALOGS),
                        json=catalog.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code == 201:
            catalog = Catalog(response.json())
            logging.info('Successfully created catalog with id {}'.format(
                                catalog.id))
            return catalog
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_catalog(self, catalog, catalogId=None):
        '''Update existing catalog.
        Args:
            catalog (Catalog)    : catalog to update.
            catalogId (str)      : catalog ID. If None, the ID defined in the
                                   catalog will be used.
        Returns:
            Modified catalog object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the catalog is wrong.
        '''
        if 'Catalog' not in str(type(catalog)):
            raise TrivoreIDSDKException('Card type is wrong')

        if catalogId is None:
            catalogId = catalog.id

        response = self._session.put(
                su.uri(self._server, self._CATALOG).format(catalogId),
                json = catalog.serialize(),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 200:
            crd = Catalog(response.json())
            logging.info('Successfully modified catalog with the id {}'
                                                    .format(crd.id))
            return crd
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_catalog(self, catalogId):
        '''Get a single catalog.
        Args:
            catalogId (str) : catalog unique identifier
        Returns:
            A catalog object.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                su.uri(self._server, self._CATALOG).format(catalogId),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 200:
            logging.info('Found catalog with id {}'.format(catalogId))
            return Catalog(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_catalog(self, catalogId):
        '''Delete catalog by id.
        Args:
            catalogId (str) : catalog unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                su.uri(self._server, self._CATALOG).format(catalogId),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 204:
            logging.info(
                    'Successfully deleted catalog with id {}'.format(catalogId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_pricing_plans(self,
                filter_fields=None,
                start_index=0,
                count=100,
                sortBy=None,
                ascending=None):
        '''Get the list of the pricing plans.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
            sortBy (str)           : sort by attribute name
            ascending (bool)       : if sort direction is ascending
        Returns:
            Page with the pagination data and the list of pricing plans.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)

        if sortBy != None:
            params['sortBy'] = sortBy
        if ascending != None:
            if ascending:
                params['sortOrder'] = 'ascending'
            else:
                params['sortOrder'] = 'descending'

        response = self._session.get(
                                su.uri(self._server, self._PRICING_PLANS),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} pricing plan objects'.format(
                        len(response.json()['resources'])))

            ls = []
            for l in response.json()['resources']:
                ls.append(PricingPlan(l))
            page = Page(response.json(), ls)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_pricing_plan(self, pricingplan):
        '''Create new pricing plan.
        Args:
            pricingplan (PricingPlan) : pricing plan to create.
        Returns:
            New pricing plan object.
        Raises:
            TrivoreIDSDKException if the type of the PricingPlan is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'PricingPlan' not in str(type(pricingplan)):
            raise TrivoreIDSDKException('PricingPlan type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._PRICING_PLANS),
                                json=pricingplan.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            pricingplan = PricingPlan(response.json())
            logging.info('Successfully created pricing plan with id {}'
                                                    .format(pricingplan.id))
            return pricingplan
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_pricing_plan(self, planId):
        '''Get the single pricing plan by id.
        Args:
            planId (str) : pricing plan unique identifier
        Returns:
            A pricing plan.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                        su.uri(self._server, self._PRICING_PLAN).format(planId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found pricing plan with id {}'.format(planId))
            return PricingPlan(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_pricing_plan(self, pricingplan, planId=None):
        '''Modify a pricing plan.
        Args:
            pricingplan (PricingPlan) : pricing plan to modify.
            planId (str)              : if None, then pricingplan ID from the
                                          PricingPlan object will be used.
        Returns:
            Modified pricing plan object.
        Raises:
            TrivoreIDSDKException if the type of the PricingPlan is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'PricingPlan' not in str(type(pricingplan)):
            raise TrivoreIDSDKException('PricingPlan type is wrong!')

        if planId is None:
            planId = pricingplan.id

        response = self._session.put(
                        su.uri(self._server, self._PRICING_PLAN).format(planId),
                        json=pricingplan.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            ls = PricingPlan(response.json())
            logging.info('Successfully modified pricing plan with the id {}'
                        .format(ls.id))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_pricing_plan(self, planId):
        '''Delete pricing plan by id.
        Args:
            planId (str) : pricing plan unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._PRICING_PLAN).format(planId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted pricing plan with id {}'
                                                    .format(planId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_products(self,
                filter_fields=None,
                start_index=0,
                count=100,
                sortBy=None,
                ascending=None):
        '''Get the list of the products.
        Args:
            filter_fields (Filter) : utils.Filter class to filter out
                                     the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500,
                                     100 by default
            sortBy (str)           : sort by attribute name
            ascending (bool)       : if sort direction is ascending
        Returns:
            Page with the pagination data and the list of products.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)

        if sortBy != None:
            params['sortBy'] = sortBy
        if ascending != None:
            if ascending:
                params['sortOrder'] = 'ascending'
            else:
                params['sortOrder'] = 'descending'

        response = self._session.get(
                                su.uri(self._server, self._PRODUCTS),
                                params=params,
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 200:
            logging.info('Found {} product objects'.format(
                        len(response.json()['resources'])))

            ls = []
            for l in response.json()['resources']:
                ls.append(Product(l))
            page = Page(response.json(), ls)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_product(self, product):
        '''Create new product.
        Args:
            product (Product) : product to create.
        Returns:
            New product object.
        Raises:
            TrivoreIDSDKException if the type of the Product is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Product' not in str(type(product)):
            raise TrivoreIDSDKException('Product type is wrong!')

        response = self._session.post(
                                su.uri(self._server, self._PRODUCTS),
                                json=product.serialize(),
                                headers=self._auth_header,
                                auth=self._auth)

        if response.status_code == 201:
            product = Product(response.json())
            logging.info('Successfully created product with id {}'
                                                    .format(product.id))
            return product
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_product(self, productId):
        '''Get the single product by id.
        Args:
            productId (str) : product unique identifier
        Returns:
            A product.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                        su.uri(self._server, self._PRODUCT).format(productId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found product with id {}'.format(productId))
            return Product(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_product(self, product, productId=None):
        '''Modify a product.
        Args:
            product (Product) : product to modify.
            productId (str)        : if None, then product ID from the
                                          Product object will be used.
        Returns:
            Modified product object.
        Raises:
            TrivoreIDSDKException if the type of the Product is wrong
            TrivoreIDException if the status code is not 200.
        '''
        if 'Product' not in str(type(product)):
            raise TrivoreIDSDKException('Product type is wrong!')

        if productId is None:
            productId = product.id

        response = self._session.put(
                        su.uri(self._server, self._PRODUCT).format(productId),
                        json=product.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            ls = Product(response.json())
            logging.info('Successfully modified product with the id {}'
                        .format(ls.id))
            return ls
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_product(self, productId):
        '''Delete product by id.
        Args:
            productId (str) : product unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                        su.uri(self._server, self._PRODUCT).format(productId),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted product with id {}'
                                                    .format(productId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
