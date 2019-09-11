#!/usr/bin/env python
# coding: utf-8

class Page(object):
    '''
    A page wrapper to wrap Trivore ID specific list results.
    '''
    def __init__(self, data, resources):
        '''
        Args:
            data (dict): the query result.
        Dictionary keys:
            'totalResults' (int) : Total number of possible results, ignoring
                                   pagination.
            'startIndex' (int)   : Start index, if pagination parameters
                                   were used.
            'itemsPerPage' (int) : Number of items per page, if pagination
                                   parameters were used.
            'resources' (list)   : list of Found resources.
        '''

        self.totalResults = data.pop('totalResults', None)
        self.startIndex = data.pop('startIndex', None)
        self.itemsPerPage = data.pop('itemsPerPage', None)
        self.resources = resources
