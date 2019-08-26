import copy
import operator

import itertools as it
import pandas as pd
import datetime as dt

from IPython.display import display, Markdown
from timeit import default_timer as timer
from dateutil.relativedelta import relativedelta

from sgmarkets_api_analytics_rates.response_curves_price import ResponseCurvesPrice
from sgmarkets_api_analytics_rates._util import Util


CHUNK_INCREMENT = relativedelta(months=1)


class RequestCurvesCustom(object):

    #TODO: put start / end date parameters in __init__ and perform isinstance checks
    def __init__(self, chunk_increment=CHUNK_INCREMENT):

        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/rates',
                   'endpoint': '/v1/curves/price'}
        self.url = Util.build_url(dic_url)
        self.chunk_increment = None #chunk_increment
        self.dic_api = None
        self.li_dic_api = None
        self.df_top = None
        self.df_leg = None
        self.customSwapCurves = {}

        self.leg_keys = [
            'ticker',
            'expiry',
            'tenor',
            'type'
        ]

    def _to_list(self, val):
        """
        """
        if isinstance(val, int):
            return [val]
        elif ',' not in val:
            return [val]
        else:
            li_val = val.split(',')
            li_val = [e.strip() for e in li_val]
            return li_val

    def info(self):
        pass

    def expand(self):

        dic_in = copy.copy(self.__dict__)
        keys = ['dic_api',
                'leg_keys',
                'df_top',
                'df_leg',
                'li_dic_api',
                'url',
                'chunk_increment']

        for key in keys:
            dic_in.pop(key)

        # change keys to format to API keys

        # build dic as a prelude to dic_api
        self.dic_input = {}
        for k, v in dic_in.items():
            if k in self.leg_keys:
                # make params in leg to list
                self.dic_input[k] = self._to_list(v)
            else:
                # top params unchanged
                self.dic_input[k] = v



        max_ = self.check_parameters()
        li_leg = []
        for i in range(max_):
            dic = {k: v[i] for k, v in self.dic_input.items()
                    if k in self.leg_keys and v[i] is not "None"}
            li_leg.append(dic)

        # modify li_leg values to include 'term' key from (expiry, tenor) pairs
        # TODO: remove for loop and construct term key earlier in the expand() method ?
        for e in li_leg:
            e['term'] = '{}x{}'.format(e['expiry'], e['tenor'])
            e.pop('expiry')
            e.pop('tenor')

        # merge top params and params in legs expanded by cartesian product
        self.dic_api = {k: v
                        for k, v in self.dic_input.items() if not k in self.leg_keys}
        self.dic_api['curves'] = li_leg
        # building term key from expiry tenor couple
        dic_top = {k: str(v)
                   for k, v in self.dic_api.items() if k != 'curves'}
        self.df_top = pd.DataFrame(dic_top, index=['Value']).T

        self.df_leg = pd.DataFrame(li_leg)
        self.li_dic_api = self.dic_api

    def check_parameters(self):
        """
        check and complete the input_dic if necessary
        """

        len_ = {k: len(v) for k, v in self.dic_input.items()
                if isinstance(v, list)}
        max_ = max(len_.items(), key=operator.itemgetter(1))[1]
        err = False
        for k, v in len_.items():
            if v is not max_:

                msg = '**<span style="color:red;">WARNING</span> -**' \
                          + 'improper combinaison of parameters resulting in an unclear strategy' \
                          + ', remainder of the division of the longest parameters and others should be 0 '
                assert (max_ % v) is 0, display(Markdown(msg))
                err = True
                self.dic_input[k] = self.dic_input[k] * int(max_ / v)

        if err:
            msg = '**<span style="color:red;">WARNING</span> -**' \
                  + 'improper combinaison of parameters resulting in an unclear strategy' \
                  + ', by default missing parameters will be filled by repetition'
            display(Markdown(msg))

        return max_

    def _split_input_by_dates(self, li_leg):
        start_date = dt.datetime.strptime(self.dic_api['startDate'], '%Y-%m-%d')
        end_date = dt.datetime.strptime(self.dic_api['endDate'], '%Y-%m-%d')

        li_date_chunk = self._chunk_dates(start_date, end_date)
        li_dic_api = []
        for start, end in li_date_chunk:
            dic_api_chunk = {k: v
                             for k, v in self.dic_input.items() if not k in self.leg_keys}
            dic_api_chunk['startDate'] = start
            dic_api_chunk['endDate'] = end
            li_leg_chunk = copy.deepcopy(li_leg)
            dic_api_chunk['curves'] = li_leg_chunk
            li_dic_api.append(dic_api_chunk)

        return li_dic_api

    #TODO: rewrite method to avoir while loop
    def _chunk_dates(self, start_date, end_date):
        nb_days = end_date - start_date
        max_nb_of_days = 2000/(len(self.dic_api['curves']))
        nb_of_chunks = max(1, int(nb_days.days/max_nb_of_days)+1)
        self.chunk_increment = relativedelta(days=(nb_days.days/nb_of_chunks))
        fmt = '%Y-%m-%d'
        _start = start_date
        _end = end_date
        chunks = []
        t0 = start_date
        t1 = min(_start + self.chunk_increment, _end)
        if t1 == _end:
            chunks.append((dt.datetime.strftime(t0,fmt), dt.datetime.strftime(t1,fmt)))
            return chunks

        while t1 <= _end:
            chunks.append((t0, t1))
            _end_chunk = t1
            t0 = t1 + relativedelta(days=1)
            t1 = _end_chunk + self.chunk_increment

        #_last_chunk = chunks[-1][-1]
        #chunks.append((_last_chunk + relativedelta(days=1), end_date))
        chunks_str = [(dt.datetime.strftime(start, fmt), dt.datetime.strftime(end, fmt)) for start, end in chunks]
        return chunks_str

    def call_api(self, api, debug=False):

        print('calling API...')
        raw_response = api.post(self.url, payload=self.dic_api)
        if debug:
            print('raw response\n{}'.format(raw_response))

        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(raw_response))

        response = ResponseCurvesPrice(li_raw_data=raw_response['curves'],
                                 obj_req=self)

        print(raw_response)
        return response


