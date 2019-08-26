import copy
import numpy as np
import pandas as pd
import json
from ._util import Util
from sgmarkets_api_auth.util import save_result


class ResponseSwapsPrice(object):

    def __init__(self, raw_data=None, obj_req=None):
        assert isinstance(raw_data, dict), \
            'Error: li_raw_data must be a list - Run call_api() again with debug=True'
        for dic_res in raw_data['swaps']:
            assert isinstance(dic_res, dict), \
                'Error: Each dic_res must be a dic - Run call_api() again with debug=True'

        raw_data = raw_data['swaps']

        self.raw_data = copy.deepcopy(raw_data)
        self.obj_req = obj_req
        self.df_res = pd.DataFrame()
        for d in raw_data:
            self.df_res = pd.concat([self.df_res,pd.DataFrame.from_dict(d, orient = 'index')], axis = 1)

        self.prices = self.df_res.T
        self.prices.index = obj_req.dates

    def _repr_html_(self):
        """
        """
        return self.df_res.to_html()

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True,
             excel=False):
        """
        """
        if name is None:
            name = 'SG_Research_Rates'

        save_result(self.df_set,
                    folder_save, name=name,
                    tagged=tagged,
                    excel=excel)

    def info(self):
        pass
