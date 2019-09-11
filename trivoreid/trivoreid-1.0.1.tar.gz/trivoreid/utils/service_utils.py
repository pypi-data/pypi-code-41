#!/usr/bin/env python
# coding: utf-8

def uri(server, api):
    return server + api

def error_response_message(response):
    try:
        errorMessage = response.json()['errorMessage']
    except:
        try:
            errorMessage = ('Unknown error message. Content: {}'
                                                .format(response.content))
        except:
            errorMessage = ('Unknown error message. Content: {}'
                                                .format(response))

    return 'status code {}, {}'.format(response.status_code, errorMessage)

def generate_parameters(filter_fields=None, start_index=0, count=100):
    params = {}

    if (filter_fields != None):
        params['filter'] = filter_fields.generate()

    if (start_index != None):
        params['startIndex'] = start_index

    if (count != None):
        params['count'] = count

    return params

def get_properties(path):
    '''
    Get properties from the property file.
    Returns:
        Dictionary with properties.
    '''
    with open(path) as file:
        lines = [line.split("=") for line in file.readlines()]

    properties = {}
    for l in lines:
        if len(l) == 2: # ignoring comments and empty lines
            properties[l[0]] = l[1].replace('\n', '')

    return properties
