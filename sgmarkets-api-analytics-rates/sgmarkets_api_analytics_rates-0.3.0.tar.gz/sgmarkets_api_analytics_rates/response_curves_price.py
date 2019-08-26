import copy
import numpy as np
import pandas as pd
import json
from ._util import Util
from sgmarkets_api_auth.util import save_result


class ResponseCurvesPrice(object):

    def __init__(self, li_raw_data=None, obj_req=None):
        assert isinstance(li_raw_data, list), \
            'Error: li_raw_data must be a list - Run call_api() again with debug=True'
        for dic_res in li_raw_data:
            assert isinstance(dic_res, dict), \
                'Error: Each dic_res must be a list - Run call_api() again with debug=True'

        raw_data = []
        for dic_res in li_raw_data:
            raw_data += dic_res['timeseries']

        self.raw_data = copy.deepcopy(raw_data)
        self.obj_req = obj_req

        self.df_req, self.df_res, self.df_set = self._build_df_res_req()
        self.dic_req_param, self.dic_res_param = self._build_dic_param()

    def _get_dates(self, df_res):
        """
        """
        dic = self.obj_req.df_top.to_dict()
        dic = dic['Value']

        if 'dates' in dic:
            res = dic['dates'].replace("'", '"')
            return json.loads(res)

        return Util.get_unique_list(df_res['date'])

    def _build_df_res_req(self):
        # df_res (response)
        li_data = []
        for e in self.raw_data:
            date = e['date']
            for f in e['curves']:
                d = {}
                d['date'] = date
                for k in f:
                    d[k] = f[k]
                li_data.append(d)

        # li_data = [e for e in self.raw_data]
        df_res = pd.DataFrame(li_data)

        # build list of dates
        li_date = self._get_dates(df_res)
        N = len(li_date)

        # df_req (request)
        # the order of results is by order of input
        # for each input the order of dates - but this is changed below
        # duplicate df_leg by number of dates
        df_leg = self.obj_req.df_leg
        df_req = pd.concat([df_leg] * N,
                           axis=0).reset_index(drop=True)

        # reorder results by date then initial order (tag)
        df_res['tag'] = range(len(df_res))
        df_res = df_res.sort_values(['date', 'tag']).reset_index(drop=True)

        # move date from df_res to df_req (more natural)
        df_req['date'] = pd.to_datetime(df_res['date'].copy())
        if 'forwardDV01Ticker' in df_res.columns:
            df_res = df_res.drop(['date', 'ticker', 'type', 'term', 'forwardDV01Ticker'], axis=1)
        else:
            df_res = df_res.drop(['date', 'ticker', 'type', 'term'], axis=1)

        # split term column into expiry and tenor columns
        df_req['expiry'] = pd.Series([e.split('x')[0] for e in df_req['term']])
        df_req['tenor'] = pd.Series([e.split('x')[1] for e in df_req['term']])
        df_req = df_req.drop('term', axis=1)

        if 'error' not in df_res:
            df_res['error'] = 'No error'
        else:
            df_res['error'] = df_res['error'].fillna('No error')

        # move col error to last position
        cols = [c for c in df_res.columns if c != 'error']+['error']
        df_res = df_res[cols]

        # replace NaN returned by API
        df_res = df_res.replace('NaN', np.nan)

        # join df_req and df_res to make df_set
        df_set = pd.concat([df_req, df_res], axis=1)

        return df_req, df_res, df_set

    def _build_dic_param(self):
        """
        """
        dic_req = self.df_req.to_dict()
        dic_req_param = {k: Util.get_unique_list(v.values())
                         for k, v in dic_req.items()}

        dic_data = self.df_res.to_dict()
        dic_res_param = {k: Util.get_unique_list(v.values())
                         for k, v in dic_data.items()}

        return dic_req_param, dic_res_param

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
