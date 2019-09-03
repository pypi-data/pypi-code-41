#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: response_parser.py
 File Created: Sunday, 24th February 2019 8:09:51 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""
import json
import asyncio
try:
    import pandas as pd
    import msgpack
except ImportError:
    pd = None


class ResponseList(list):

    def __getattr__(self, name):
        return [x[name] for x in self]


class ResponseParser(object):
    """
        Class definition of a how to parse a influx response
    """
    def parse(self, response):
        if(asyncio.isfuture(response)):
            return self.parse_response_async(response)
        return self.parse_response(response)

    def parse_response(self, response):
        """
            Parse a response
        """
        raise NotImplementedError('This is a abstract definition, please implement your own')

    async def parse_response_async(self, response):
        """
            Async wrapper for parse response
        """
        response = await response
        return self.parse_response(response)


class StringParse(ResponseParser):
    """
        Class definition for parsing to string
    """

    def parse_response(self, response):
        """
            Parse response to a string
        """
        return response.body.decode("utf-8")


class JsonParse(ResponseParser):
    """
        Class definition for parsing json string to dict
    """

    @classmethod
    def from_json_string(cls, response):
        return [json.loads(x) for x in response.body.decode("utf-8").split('\n') if x]

    def parse_response(self, response):
        """
            Parse response to a dict
        """
        response = self.from_json_string(response)
        parsed_response = ResponseList()
        for body in response:
            for r in body.get('results', []):
                for s in r.get('series', []):
                    columns = s.get('columns', [])
                    for r in s.get('values', []):
                        row = {}
                        for i, c in enumerate(r):
                            try:
                                row[columns[i]] = c
                            except IndexError:
                                pass
                        parsed_response.append(row)

        return parsed_response




class MsgpackParse(ResponseParser):

    @classmethod
    def from_msgpack_string(cls, response):
        return msgpack.unpackb(response, use_list=False, raw=False)

    def parse_response(self, response):
        """
            Parse response to a dict
        """
        return self.from_msgpack_string(response.body)


class DataframeParser(ResponseParser):
    """
        Class definition for parsing to a pandas dataframe
    """

    def parse_response(self, response):
        """
            Parse response into a pandas dataframe
        """
        response_converted = [json.loads(x) for x in response.body.decode("utf-8").split('\n') if x]
        response_converted = self.response_to_dataframe(response_converted)
        return response_converted

    def response_to_dataframe(self, response):
        """
            Takes a 200 OK response object and parses the data into a dataframe
        """
        result = None
        # import pdb; pdb.set_trace()
        for body in response:
            for r in body.get('results', []):
                for s in r.get('series', []):
                    df = pd.DataFrame(s['values'], columns=s['columns'])
                    if('time' in df.columns):
                        df.time = pd.to_datetime(df.time)
                        df = df.set_index('time')
                    
                    tags = s.get('tags', None)
                    if(tags):
                        col_names = list(df.columns) 
                        for k, v in tags.items():
                            col_names = [x + '-' + v for x in col_names]
                        df.columns = col_names    



                    if(result is None):
                        result = df
                    else:
                        result = pd.concat([result, df], sort=True)

        # Concat all results:
        if(result is None):
            return self.get_empty_dataframe()

        return result

    def get_empty_dataframe(self):
        """
            returns a empty dataframe
        """
        return pd.DataFrame()


default_parser = JsonParse
if(pd is not None):
    default_parser = DataframeParser