#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta

class Enterprise(object):
    '''
    Class that represents an enterprise object.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): enterprise fields
        Dictionary keys:
            'businessId' (str) - business ID
            'vatId' (str)
            'tradeName' (str)
            'domicile' (str)
            'leiCode' (str)
            'duns' (str)
            'parallelTradeNames' (list)
            'auxiliaryTradeNames' (list)
            'tradeRegisterNumber' (str)
            'taxIdentificationNumber' (str)
            'general' (dict) ContactInfo fields
            'sales' (dict) ContactInfo fields
            'service' (dict) ContactInfo fields
            'customerSupport' (dict) ContactInfo fields
            'meta' (dict) meta data
        '''
        self.businessId = data.pop('businessId', None)
        self.vatId = data.pop('vatId', None)
        self.tradeName = data.pop('tradeName', None)
        self.domicile = data.pop('domicile', None)
        self.leiCode = data.pop('leiCode', None)
        self.parallelTradeNames = data.pop('parallelTradeNames', None)
        self.auxiliaryTradeNames = data.pop('auxiliaryTradeNames', None)
        self.tradeRegisterNumber = data.pop('tradeRegisterNumber', None)
        self.taxIdentificationNumber = data.pop('taxIdentificationNumber', None)
        self.general = EnterpriseContactInfo(data.pop('general', {}))
        self.sales = EnterpriseContactInfo(data.pop('sales', {}))
        self.service = EnterpriseContactInfo(data.pop('service', {}))
        self.customerSupport = EnterpriseContactInfo(data.pop('customerSupport', {}))
        self.meta = Meta(data.pop('meta', {}))

    def serialize(self):
        '''
        Return JSON serializable object.
        '''
        return {
            'businessId'                : self.businessId,
            'vatId'                     : self.vatId,
            'tradeName'                 : self.tradeName,
            'domicile'                  : self.domicile,
            'leiCode'                   : self.leiCode,
            'parallelTradeNames'        : self.parallelTradeNames,
            'auxiliaryTradeNames'       : self.auxiliaryTradeNames,
            'tradeRegisterNumber'       : self.tradeRegisterNumber,
            'taxIdentificationNumber'   : self.taxIdentificationNumber,
            'general'                   : self.general.serialize(),
            'sales'                     : self.sales.serialize(),
            'service'                   : self.service.serialize(),
            'customerSupport'           : self.customerSupport.serialize(),
            'meta'                      : self.meta.serialize()
        }

class EnterpriseContactInfo(object):
    '''
    Class that represents a customer support contact info object.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict): contact info fields
        Dictionary keys:
            'phone' (str) - business ID
            'email' (str)
            'website' (str)
            'contacts' (str)
        '''
        self.phone = data.pop('phone', None)
        self.email = data.pop('email', None)
        self.website = data.pop('website', None)
        self.contacts = data.pop('contacts', None)

    def serialize(self):
        '''
        Return JSON serializable object.
        '''
        return {
            'phone'       : self.phone,
            'email'       : self.email,
            'website'     : self.website,
            'contacts'    : self.contacts
        }
