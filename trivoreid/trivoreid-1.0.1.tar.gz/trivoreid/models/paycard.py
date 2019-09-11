#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta

class Paycard(object):
    '''
    Wrapper for the user paycard.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict)      : self.paycard data
        Dectionary values:
            id               : Internal ID.
            userId           : ID of the user the paycard belongs to.
            namespaceId      : ID of the namespace the paycard belongs to.
            name             : The name of the paycard
            state            : The state of the paycard (ACTIVE or INACTIVE)
            priority         : Optional priority when listing cards. From 0 to 8
            method           : Card method, cash/creditcard/debitcard/operator/
                               blockchain/other
            cardBrand        : Card brand, Amex/Mastercard/Visa/ApplePay/
                               GooglePay/MobilePay/Discover
            cardSubBrand     : Card Subbrand, Basic/Platinum/Gold/Maestro/
                               Electron
            cardIssuer       : Card issuer, for example bank name
            cardIssuerCode   : Card issuer code, for example bank swift code
            cardType         : Card type, credit/debit/virtual/other
            validFrom        : Valid From, refers to entity validity in user
                               settings, not to card.
                               For example : 2020-10-20T07:17:17.606Z
            validTo          : Valid To, refers to entity validity in user
                               settings, not to card.
                               For example : 2018-10-20T07:17:17.606Z
            leadingDigits    : The leading six digits of the card
            lastDigits       : The last four digits of the card
            expirationYear   : Expiration year
            expirationMonth  : Expiration month
            cardData         : list of CardDataEntries objects
            cardCapabilities : list of CardDataEntries objects
            externalCode     : External code for application specific usage
            externalRef      : External reference for application specific usage
            internalRef      : Internal reference for application specific usage
            nameOnCard       : For application specific usage
            meta             : Meta data
            cardValidUntil   : Card valid until. PCI DSS requirement
            cardNumber       : WARNING! The card number is highly secret and
                               personal. You should probably not use it here.
                               The number on the card. PCI DSS requirement.
                               Reading this property requires either the
                               PAYCARD_NUMBER_VIEW or the PAYCARD_NUMBER_MODIFY
                               permission and writing requires the
                               PAYCARD_NUMBER_MODIFY permission.
            cardValidToISODate : Gets the valid until date as an ISO datetime
                                 without timezone. Returns null if valid until
                                 is null, blank or in invalid format. This is a
                                 generated property and cannot be used in
                                 filters.
        '''

        self.cardData = []
        for d in data.pop('cardData', []):
            self.cardData.append(CardDataEntry(d))

        self.cardCapabilities = []
        for c in data.pop('cardCapabilities', []):
            self.cardCapabilities.append(CardDataEntry(c))

        self.id = data.pop('id', None)
        self.userId = data.pop('userId', None)
        self.namespaceId = data.pop('namespaceId', None)
        self.name = data.pop('name', None)
        self.state = data.pop('state', None)
        self.priority = data.pop('priority', None)
        self.method = data.pop('method', None)
        self.cardBrand = data.pop('cardBrand', None)
        self.cardSubBrand = data.pop('cardSubBrand', None)
        self.cardIssuer = data.pop('cardIssuer', None)
        self.cardIssuerCode = data.pop('cardIssuerCode', None)
        self.cardType = data.pop('cardType', None)
        self.validFrom = data.pop('validFrom', None)
        self.validTo = data.pop('validTo', None)
        self.leadingDigits = data.pop('leadingDigits', None)
        self.lastDigits = data.pop('lastDigits', None)
        self.expirationYear = data.pop('expirationYear', None)
        self.expirationMonth = data.pop('expirationMonth', None)
        self.externalCode = data.pop('externalCode', None)
        self.externalRef = data.pop('externalRef', None)
        self.internalRef = data.pop('internalRef', None)
        self.nameOnCard = data.pop('nameOnCard', None)
        self.meta = Meta(data.pop('meta', {}))
        self.cardValidUntil = data.pop('cardValidUntil', None)
        self.cardNumber = data.pop('cardNumber', None)
        self.cardValidToISODate = data.pop('cardValidToISODate', None)

    def serialize(self):
        '''
        Return JSON serializable dictionary with Paycard fields.
        '''

        cardData = []
        for d in self.cardData:
            cardData.append(d.serialize())

        cardCapabilities = []
        for c in self.cardCapabilities:
            cardCapabilities.append(c.serialize())

        return {
            'id'                    : self.id,
            'userId'                : self.userId,
            'namespaceId'           : self.namespaceId,
            'name'                  : self.name,
            'state'                 : self.state,
            'priority'              : self.priority,
            'method'                : self.method,
            'cardBrand'             : self.cardBrand,
            'cardSubBrand'          : self.cardSubBrand,
            'cardIssuer'            : self.cardIssuer,
            'cardIssuerCode'        : self.cardIssuerCode,
            'cardType'              : self.cardType,
            'validFrom'             : self.validFrom,
            'validTo'               : self.validTo,
            'leadingDigits'         : self.leadingDigits,
            'lastDigits'            : self.lastDigits,
            'expirationYear'        : self.expirationYear,
            'expirationMonth'       : self.expirationMonth,
            'cardData'              : cardData,
            'cardCapabilities'      : cardCapabilities,
            'externalCode'          : self.externalCode,
            'externalRef'           : self.externalRef,
            'internalRef'           : self.internalRef,
            'nameOnCard'            : self.nameOnCard,
            'meta'                  : self.meta.serialize(),
            'cardValidUntil'        : self.cardValidUntil,
            'cardNumber'            : self.cardNumber,
            'cardValidToISODate'    : self.cardValidToISODate
        }

class CardDataEntry(object):
    '''
    Wrapper for a single card data entry.
    NB! Entries with the same keys are not allowed!
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (list) : list of card data entries
        Dictionary values:
            key     (str)
            value   (str)
        '''
        self.key = data.pop('key', None)
        self.value = data.pop('value', None)

    def serialize(self):
        return {
            'key'   : self.key,
            'value' : self.value
        }

class PanToken(object):
    '''
    Wrapper for the PAN token.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : list of card data entries
        Dictionary values:
            id        : PAN token unique identifier
            paycardId : paycard unique identifier
            token     : token value
            issuer    : PAN token issuer
            timestamp : timestamp
            'meta'    : meta data
        '''
        self.id = data.pop('id', None)
        self.paycardId = data.pop('paycardId', None)
        self.token = data.pop('token', None)
        self.issuer = data.pop('issuer', None)
        self.timestamp = data.pop('timestamp', None)
        self.meta = Meta(data.pop('meta', {}))

    def serialize(self):
        return {
            'id'         : self.id,
            'paycardId'  : self.paycardId,
            'token'      : self.token,
            'issuer'     : self.issuer,
            'timestamp'  : self.timestamp,
            'meta'       : self.meta.serialize()
        }
