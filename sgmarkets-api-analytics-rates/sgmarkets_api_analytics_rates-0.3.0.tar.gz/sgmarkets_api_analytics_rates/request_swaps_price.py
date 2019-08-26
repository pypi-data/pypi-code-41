import copy
import operator

import itertools as it
import pandas as pd
import datetime as dt

from IPython.display import display, Markdown
from timeit import default_timer as timer
from dateutil.relativedelta import relativedelta

from sgmarkets_api_analytics_rates.response_swaps_price import ResponseSwapsPrice
from sgmarkets_api_analytics_rates._util import Util


CHUNK_INCREMENT = relativedelta(months=1)


class RequestSwapsPrice(object):

    #TODO: put start / end date parameters in __init__ and perform isinstance checks
    def __init__(self, chunk_increment=CHUNK_INCREMENT):

        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/rates',
                   'endpoint': '/v1/swaps/price'}
        self.url = Util.build_url(dic_url)
        self.dic_api = {}
        self.bday = True
        self.dic_input = {}
        self.df_leg = None
        self.date = None
        self.leg_keys = [
            #'start_date',
            #'end_date',
            #'date',
            'issueDate',
            'maturityDate',
            'fixedCoupon',
            'fixedFrequency',
            'fixedBasis',
            'fixedDiscountTicker',
            'floatingTicker',
            'floatingDiscountTicker',
            'daysToSettle',
            'notional',
        ]
        self.start_date = None
        self.end_date = None


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

    def converting_dates(self,dic_in):
        if not 'date' in dic_in.keys():
            dic_in['date'] = None
        if not 'start_date' in dic_in.keys():
             dic_in['start_date'] = None
        if not 'end_date' in dic_in.keys():
                dic_in['end_date'] = None
        assert dic_in['date'] or (dic_in['start_date'] and dic_in['end_date']), "User has to either enter a date, a list of dates or a start date and an end date. See the example notebook."
        if not dic_in['date']:
            assert isinstance(dic_in['start_date'],str) and isinstance(dic_in['start_date'],str), "Start date and end date should be of type str with format 'YYYY-mm-dd. Here: start_date:{} , end_date:{}".format(dic_in.start_date, dic_in.end_date)
            if self.bday:
                dic_in['date']= pd.bdate_range(start = dic_in['start_date'], end=dic_in['end_date']).strftime('%Y-%m-%d').tolist()
            else:
                dic_in['date'] = pd.date_range(start=dic_in['start_date'], end=dic_in['end_date']).strftime(
                    '%Y-%m-%d').tolist()
        else: # or date_range
            if not isinstance(dic_in['date'], list):
                dic_in['date'] = [dic_in['date']]
            assert all([isinstance(d, str) for d in dic_in['date']]), "date should be either a string or a list of string with format 'YYYY-mm-dd'. Here date: {}".format(dic_in.date)
        return dic_in




    def expand(self):

        dic_in = copy.copy(self.__dict__)
        keys = ['dic_api',
                'leg_keys',
                'df_leg',
                'url',
                'bday']

        for key in keys:
            dic_in.pop(key)

        dic_in = self.converting_dates(dic_in)
        # change keys to format to API keys
        remove_keys = {
            'start_date',
            'end_date',

        }

        for key in remove_keys:
            if key in dic_in.keys():
                dic_in.pop(key)

        # build dic as a prelude to dic_api

        for k, v in dic_in.items():
            if k in self.leg_keys:
                # make params in leg to list
                self.dic_input[k] = v
        li_leg = []
        for d in dic_in['date']:
            dic = {'date':d}
            dic.update(self.dic_input)
            li_leg.append(dic)

        self.dates = dic_in['date']


        # merge top params and params in legs expanded by cartesian product

        self.dic_api['swaps'] = li_leg
        # building term key from expiry tenor couple

        self.df_leg = pd.DataFrame(li_leg)

    def call_api(self, api, debug=False):
        t0 = timer()
        print('calling API...')
        #raw_response = []
        raw_response = api.post(self.url, payload=self.dic_api)
        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(raw_response))
        t1 = timer()
        print('done in {:.2f} s'.format(t1 - t0))

        response = ResponseSwapsPrice(raw_data=raw_response,
                                 obj_req=self)


        return response


