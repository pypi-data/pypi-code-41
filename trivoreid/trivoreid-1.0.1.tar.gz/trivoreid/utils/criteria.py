#!/usr/bin/env python
# coding: utf-8

from trivoreid.exceptions import TrivoreIDSDKException

class Filter:
    '''
    Object to generate the query filter.
    '''

    EQUAL = ' eq '
    NOT_EQUAL = ' ne '
    CONTAINS = ' co '
    STARTS_WITH = ' sw '
    ENDS_WITH = ' ew '
    PRESENT = ' pr '
    GREATER_THAN = ' gt '
    GREATER_OR_EQUAL_THAN = ' ge '
    LESS_THAN = ' lt '
    LESS_OR_EQUAL_THAN = ' le '
    _AND = ' and '
    _OR = ' or '

    def __init__(self,
                 filter_type = None,
                 attribute = None,
                 value = None):
        '''
        Args:
            filter_type (Filter) : enum from the Filter class
            attribute (str)      : the name of the attribute
            value                : value of the attribute
        '''
        self.filter_type = filter_type
        self.attribute = attribute
        self.value = value

    def and_filters(self, filter1, filter2):
        '''
        Combine two filters.
        Args:
            filter1 (Filter)
            filter2 (Filter)
        '''
        self._check_filter_type(filter1)
        self._check_filter_type(filter2)
        return Filter(Filter._AND, None, [filter1, filter2])

    def or_filters(self, filter1, filter2):
        '''
        Combine two filters.
        Args:
            filter1 (Filter)
            filter2 (Filter)
        '''
        self._check_filter_type(filter1)
        self._check_filter_type(filter2)
        return Filter(Filter._OR, None, [filter1, filter2])

    def generate(self):
        '''
        Generate filter parameter.
        Returns:
            Filter string.
        '''
        if type(self.value) == list:
            if len(self.value) != 2:
                raise TrivoreIDSDKException('Filter contains {} values'
                                            .format(len(self.value)))
            return "({}) {} ({})".format(self.value[0].generate(),
                                         self.filter_type,
                                         self.value[1].generate())
        elif 'Filter' in str(type(self.value)):
            return self.value.generate()
        else:
            if self.filter_type == self.PRESENT:
                return (self.attribute + self.filter_type)
            if type(self.value) is int:
                return (self.attribute + self.filter_type + str(self.value))
            else:
                return (self.attribute + self.filter_type
                                                + '"' + str(self.value) + '"')

    def _check_filter_type(self, f):
        if 'Filter' not in str(type(f)):
            raise TrivoreIDSDKException('Filter type is wrong!')
