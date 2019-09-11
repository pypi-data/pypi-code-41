#!/usr/bin/env python
# coding: utf-8

class Catalog(object):
    '''
    Wrapper for the Catalog.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : catalog fields
        Dictionary keys:
            'id' (str)
            'ownerId' (str)
            'accessControlIds' (list)
            'name' (str)
            'products' (list) list of CatalogItem objects
            'customFields' (dict)
        '''
        self.products = []
        for item in data.pop('products', []):
            self.products.append(CatalogItem(item))

        self.id = data.pop('id', None)
        self.ownerId = data.pop('ownerId', None)
        self.accessControlIds = data.pop('id', [])
        self.name = data.pop('name', None)
        self.customFields = data.pop('customFields', {})

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        products = []
        for item in self.products:
            products.append(item.serialize())

        return {
            'id'                : self.id,
            'ownerId'           : self.ownerId,
            'accessControlIds'  : self.accessControlIds,
            'name'              : self.name,
            'products'          : products,
            'customFields'      : self.customFields
            }

class CatalogItem(object):
    '''
    Wrapper for the Catalog Item.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : catalog item fields
        Dictionary keys:
            'productId' (str)
            'productSku' (str)
            'productValuesInherited' (boolean) True: Empty or null fields values
                                               are replaced with values from
                                               original product
            'descriptions' (dict) localised product names and descriptions.
                                  NB! Values must have dictionary type.
            'customFields' (dict)
            'sellable' (list) List of Valid objects. Times when sellable. If
                              null or empty, base product sellable value is
                              used.
            'usable' (list) List of Valid objects. times when usable. If null or
                            empty, base product usable value is used.
            'provider' (str) product provider. If null, base product provider
                             value is used.
            'pricingPlans' (list) pricing plan ID values. If null or empty,
                                  base product value is used.
            'validityLength' (int) product validity time length, in seconds.
                                   Time start depends on validityStartFrom.
            'validityStartFrom' (str) product validity start from option.
                                      PURCHASE or FIRST_USE
        '''
        self.sellable = []
        for validity in data.pop('sellable', []):
            self.sellable.append(Validity(validity))

        self.usable = []
        for validity in data.pop('usable', []):
            self.usable.append(Validity(validity))

        self.productId = data.pop('productId', None)
        self.productSku = data.pop('productSku', None)
        self.productValuesInherited = data.pop('productValuesInherited', None)
        self.descriptions = data.pop('descriptions', {})
        self.customFields = data.pop('customFields', {})
        self.provider = data.pop('provider', None)
        self.pricingPlans = data.pop('pricingPlans', [])
        self.validityLength = data.pop('validityLength', None)
        self.validityStartFrom = data.pop('validityStartFrom', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        sellable = []
        for validity in self.sellable:
            sellable.append(validity.serialize())

        usable = []
        for validity in self.usable:
            usable.append(validity.serialize())

        return {
            'productId'                 : self.productId,
            'productSku'                : self.productSku,
            'productValuesInherited'    : self.productValuesInherited,
            'descriptions'              : self.descriptions,
            'customFields'              : self.customFields,
            'provider'                  : self.provider,
            'pricingPlans'              : self.pricingPlans,
            'validityLength'            : self.validityLength,
            'validityStartFrom'         : self.validityStartFrom,
            'sellable'                  : sellable,
            'usable'                    : usable
            }

class Validity(object):
    '''
    Wrapper for the Validity.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : validity fields
        Dictionary keys:
            'title' (str) short title for this validity configuration.
            'validFrom' (str) valid starting from this datetime.
            'validUntil' (str) valid until this datetime.
            'daysOfWeek' (list) if set, is valid only on these days.
            'zoneId' (str) time zone for daysOfWeek check.
            'exceptions' (list) exceptions to validity. If any exception is
                                currently valid, this is not valid.
            'validNow' (bool)
        '''
        self.title = data.pop('title', None)
        self.validFrom = data.pop('validFrom', None)
        self.validUntil = data.pop('validUntil', None)
        self.daysOfWeek = data.pop('daysOfWeek', [])
        self.zoneId = data.pop('zoneId', None)
        self.exceptions = data.pop('exceptions', [])
        self.validNow = data.pop('validNow', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'title'         : self.title,
            'validFrom'     : self.validFrom,
            'validUntil'    : self.validUntil,
            'daysOfWeek'    : self.daysOfWeek,
            'zoneId'        : self.zoneId,
            'exceptions'    : self.exceptions,
            'validNow'      : self.validNow
            }

class PricingPlan(object):
    '''
    Wrapper for the Pricing Plan.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : pricing plan fields
        Dictionary keys:
            'id' (str)
            'ownerId' (str)
            'accessControlIds' (list)
            'pricings' (list)
            'customFields' (dict)
            'enabled' (bool)
            'title' (str)
            'description' (str)
            'availability' (list)
            'publishDate' (str)
            'unpublishDate' (str)
        '''
        self.pricings = []
        for pricing in data.pop('pricings', []):
            self.pricings.append(Pricing(pricing))

        self.availability = []
        for a in data.pop('availability', []):
            self.availability.append(Validity(a))

        self.id = data.pop('id', None)
        self.ownerId = data.pop('ownerId', None)
        self.accessControlIds = data.pop('id', [])
        self.customFields = data.pop('customFields', {})
        self.enabled = data.pop('enabled', None)
        self.title = data.pop('title', None)
        self.description = data.pop('description', None)
        self.publishDate = data.pop('publishDate', None)
        self.unpublishDate = data.pop('unpublishDate', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        pricings = []
        for pricing in self.pricings:
            pricings.append(pricing.serialize())

        availability = []
        for a in self.availability:
            availability.append(pricing.serialize())

        return {
            'id'                : self.id,
            'ownerId'           : self.ownerId,
            'accessControlIds'  : self.accessControlIds,
            'customFields'      : self.customFields,
            'pricings'          : pricings,
            'availability'      : availability,
            'enabled'           : self.enabled,
            'title'             : self.title,
            'description'       : self.description,
            'publishDate'       : self.publishDate,
            'unpublishDate'     : self.unpublishDate
            }

class Pricing(object):
    '''
    Wrapper for the Pricing.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : pricing fields
        Dictionary keys:
            'enabled' (bool)
            'title' (str)
            'description' (str)
            'price' (double)
            'currency' (str) ISO 4217 currency code
            'vatIncluded' (bool)
            'vatPercent' (double)
            'codeDiscounts' (list)
            'volumeDiscounts' (list)
            'customerSegmentDiscounts' (list)
            'paymentMethodDiscounts' (list)
            'variableDiscounts' (list)
            'codeDiscountStacking' (bool)
            'volumeDiscountStacking' (bool)
            'customerSegmentDiscountStacking' (bool)
            'variableDiscountStacking' (bool)
        '''
        self.codeDiscounts = []
        for d in data.pop('codeDiscounts', []):
            self.codeDiscounts.append(CodeDiscount(d))

        self.volumeDiscounts = []
        for d in data.pop('volumeDiscounts', []):
            self.volumeDiscounts.append(VolumeDiscount(d))

        self.customerSegmentDiscounts = []
        for d in data.pop('customerSegmentDiscounts', []):
            self.customerSegmentDiscounts.append(CustomerSegmentDiscount(d))

        self.paymentMethodDiscounts = []
        for d in data.pop('paymentMethodDiscounts', []):
            self.paymentMethodDiscounts.append(PaymentMethodDiscount(d))

        self.variableDiscounts = []
        for d in data.pop('variableDiscounts', []):
            self.variableDiscounts.append(VariableDiscount(d))

        self.enabled = data.pop('enabled', None)
        self.title = data.pop('title', None)
        self.description = data.pop('description', None)
        self.price = data.pop('price', None)
        self.currency = data.pop('currency', None)
        self.vatIncluded = data.pop('vatIncluded', None)
        self.vatPercent = data.pop('vatPercent', None)
        self.codeDiscountStacking = data.pop('codeDiscountStacking', None)
        self.volumeDiscountStacking = data.pop('volumeDiscountStacking', None)
        self.customerSegmentDiscountStacking = data.pop(
                                        'customerSegmentDiscountStacking', None)
        self.variableDiscountStacking = data.pop(
                                        'variableDiscountStacking', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        codeDiscounts = []
        for d in self.codeDiscounts:
            codeDiscounts.append(d.serialize())

        volumeDiscounts = []
        for d in self.volumeDiscounts:
            volumeDiscounts.append(d.serialize())

        customerSegmentDiscounts = []
        for d in self.customerSegmentDiscounts:
            customerSegmentDiscounts.append(d.serialize())

        paymentMethodDiscounts = []
        for d in self.paymentMethodDiscounts:
            paymentMethodDiscounts.append(d.serialize())

        variableDiscounts = []
        for d in self.variableDiscounts:
            variableDiscounts.append(d.serialize())

        return {
            'enabled' : self.enabled,
            'title' : self.title,
            'description' : self.description,
            'price' : self.price,
            'currency' : self.currency,
            'vatIncluded' : self.vatIncluded,
            'vatPercent' : self.vatPercent,
            'codeDiscountStacking' : self.codeDiscountStacking,
            'volumeDiscountStacking' : self.volumeDiscountStacking,
            'customerSegmentDiscountStacking' : self.customerSegmentDiscountStacking,
            'variableDiscountStacking' : self.variableDiscountStacking,
            'codeDiscounts' : codeDiscounts,
            'volumeDiscounts' : volumeDiscounts,
            'customerSegmentDiscounts' : customerSegmentDiscounts,
            'paymentMethodDiscounts' : paymentMethodDiscounts,
            'variableDiscounts' : variableDiscounts
            }

class CodeDiscount(object):
    '''
    Wrapper for the Code Discount.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : code discount fields
        Dictionary keys:
            'title' (str)
            'discountPercentage' (double)
            'discountAmount' (double)
            'discountAmountPerItem' (double)
            'limitedToApiClients' (list)
            'limitedToUsers' (list)
            'limitedToUserGroups' (list)
            'code' (str)
        '''
        self.title = data.pop('title', None)
        self.discountPercentage = data.pop('discountPercentage', None)
        self.discountAmount = data.pop('discountAmount', None)
        self.discountAmountPerItem = data.pop('discountAmountPerItem', None)
        self.limitedToApiClients = data.pop('limitedToApiClients', [])
        self.limitedToUsers = data.pop('limitedToUsers', [])
        self.limitedToUserGroups = data.pop('limitedToUserGroups', [])
        self.code = data.pop('code', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'title' : self.title,
            'discountPercentage' : self.discountPercentage,
            'discountAmount' : self.discountAmount,
            'discountAmountPerItem' : self.discountAmountPerItem,
            'limitedToApiClients' : self.limitedToApiClients,
            'limitedToUsers' : self.limitedToUsers,
            'limitedToUserGroups' : self.limitedToUserGroups,
            'code' : self.code
            }

class VolumeDiscount(object):
    '''
    Wrapper for the Volume Discount.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : volume discount fields
        Dictionary keys:
            'title' (str)
            'discountPercentage' (double)
            'discountAmount' (double)
            'discountAmountPerItem' (double)
            'limitedToApiClients' (list)
            'limitedToUsers' (list)
            'limitedToUserGroups' (list)
            'rangeStart' (int)
            'rangeEnd' (int)
        '''
        self.title = data.pop('title', None)
        self.discountPercentage = data.pop('discountPercentage', None)
        self.discountAmount = data.pop('discountAmount', None)
        self.discountAmountPerItem = data.pop('discountAmountPerItem', None)
        self.limitedToApiClients = data.pop('limitedToApiClients', [])
        self.limitedToUsers = data.pop('limitedToUsers', [])
        self.limitedToUserGroups = data.pop('limitedToUserGroups', [])
        self.rangeStart = data.pop('rangeStart', None)
        self.rangeEnd = data.pop('rangeEnd', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'title' : self.title,
            'discountPercentage' : self.discountPercentage,
            'discountAmount' : self.discountAmount,
            'discountAmountPerItem' : self.discountAmountPerItem,
            'limitedToApiClients' : self.limitedToApiClients,
            'limitedToUsers' : self.limitedToUsers,
            'limitedToUserGroups' : self.limitedToUserGroups,
            'rangeStart' : self.rangeStart,
            'rangeEnd' : self.rangeEnd
            }

class CustomerSegmentDiscount(object):
    '''
    Wrapper for the Customer Segment Discount.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : customer segment discount fields
        Dictionary keys:
            'title' (str)
            'discountPercentage' (double)
            'discountAmount' (double)
            'discountAmountPerItem' (double)
            'limitedToApiClients' (list)
            'limitedToUsers' (list)
            'limitedToUserGroups' (list)
            'customerSegment' (str)
        '''
        self.title = data.pop('title', None)
        self.discountPercentage = data.pop('discountPercentage', None)
        self.discountAmount = data.pop('discountAmount', None)
        self.discountAmountPerItem = data.pop('discountAmountPerItem', None)
        self.limitedToApiClients = data.pop('limitedToApiClients', [])
        self.limitedToUsers = data.pop('limitedToUsers', [])
        self.limitedToUserGroups = data.pop('limitedToUserGroups', [])
        self.customerSegment = data.pop('customerSegment', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'title' : self.title,
            'discountPercentage' : self.discountPercentage,
            'discountAmount' : self.discountAmount,
            'discountAmountPerItem' : self.discountAmountPerItem,
            'limitedToApiClients' : self.limitedToApiClients,
            'limitedToUsers' : self.limitedToUsers,
            'limitedToUserGroups' : self.limitedToUserGroups,
            'customerSegment' : self.customerSegment
            }

class PaymentMethodDiscount(object):
    '''
    Wrapper for the Payment Method Discount.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : payment method discount fields
        Dictionary keys:
            'title' (str)
            'discountPercentage' (double)
            'discountAmount' (double)
            'discountAmountPerItem' (double)
            'limitedToApiClients' (list)
            'limitedToUsers' (list)
            'limitedToUserGroups' (list)
            'paymentMethod' (str)
        '''
        self.title = data.pop('title', None)
        self.discountPercentage = data.pop('discountPercentage', None)
        self.discountAmount = data.pop('discountAmount', None)
        self.discountAmountPerItem = data.pop('discountAmountPerItem', None)
        self.limitedToApiClients = data.pop('limitedToApiClients', [])
        self.limitedToUsers = data.pop('limitedToUsers', [])
        self.limitedToUserGroups = data.pop('limitedToUserGroups', [])
        self.paymentMethod = data.pop('paymentMethod', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'title' : self.title,
            'discountPercentage' : self.discountPercentage,
            'discountAmount' : self.discountAmount,
            'discountAmountPerItem' : self.discountAmountPerItem,
            'limitedToApiClients' : self.limitedToApiClients,
            'limitedToUsers' : self.limitedToUsers,
            'limitedToUserGroups' : self.limitedToUserGroups,
            'paymentMethod' : self.paymentMethod
            }

class VariableDiscount(object):
    '''
    Wrapper for the Variable Discount.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : variable discount fields
        Dictionary keys:
            'title' (str)
            'discountPercentageEval' (str)
            'discountAmountEval' (str)
            'discountAmountPerItemEval' (str)
        '''
        self.title = data.pop('title', None)
        self.discountPercentageEval = data.pop('discountPercentageEval', None)
        self.discountAmountEval = data.pop('discountAmountEval', None)
        self.discountAmountPerItemEval = data.pop(
                                            'discountAmountPerItemEval', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'title' : self.title,
            'discountPercentageEval' : self.discountPercentageEval,
            'discountAmountEval' : self.discountAmountEval,
            'discountAmountPerItemEval' : self.discountAmountPerItemEval
            }

class Product(object):
    '''
    Wrapper for the Product.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : product fields
        Dictionary keys:
            'id' (str)
            'ownerId' (str)
            'accessControlIds' (list)
            'sku' (str)
            'descriptions' (dict) localised product names and descriptions
            'customFields' (dict)
            'sellable' (list) times when sellable. If null or empty, base
                              product sellable value is used.
            'usable' (list) times when usable.
            'provider' (str) product provider.
            'pricingPlans' (list) pricing plan ID values.
            'validityLength' (int) product validity time length, in seconds.
                                   Time start depends on validityStartFrom.
            'validityStartFrom' (str) product validity start from option.
                                      PURCHASE or FIRST_USE
        '''
        self.sellable = []
        for validity in data.pop('sellable', []):
            self.sellable.append(Validity(validity))

        self.usable = []
        for validity in data.pop('usable', []):
            self.usable.append(Validity(validity))

        self.id = data.pop('id', None)
        self.ownerId = data.pop('ownerId', None)
        self.accessControlIds = data.pop('id', [])
        self.productId = data.pop('productId', None)
        self.sku = data.pop('sku', None)
        self.descriptions = data.pop('descriptions', {})
        self.customFields = data.pop('customFields', {})
        self.provider = data.pop('provider', None)
        self.pricingPlans = data.pop('pricingPlans', [])
        self.validityLength = data.pop('validityLength', None)
        self.validityStartFrom = data.pop('validityStartFrom', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        sellable = []
        for validity in self.sellable:
            sellable.append(validity.serialize())

        usable = []
        for validity in self.usable:
            usable.append(validity.serialize())

        return {
            'id'                        : self.id,
            'ownerId'                   : self.ownerId,
            'accessControlIds'          : self.accessControlIds,
            'sku'                       : self.sku,
            'descriptions'              : self.descriptions,
            'customFields'              : self.customFields,
            'provider'                  : self.provider,
            'pricingPlans'              : self.pricingPlans,
            'validityLength'            : self.validityLength,
            'validityStartFrom'         : self.validityStartFrom,
            'sellable'                  : sellable,
            'usable'                    : usable
            }
