from sgmarkets_api_analytics_rates.response_curves_price import ResponseCurvesPrice
import pandas as pd
from ._util import Util
import copy
import functools
from sgmarkets_api_auth.util import save_result


class SliceCurvesPrice(object):

    def __init__(self,
                 obj_res,
                 x=None,
                 y=None,
                 z=None,
                 dic_req_fix=None,
                 value=None,
                 y_pos='index',  # index or column
                 ):
        """
        """
        # print(type(obj_res))
        assert isinstance(obj_res, ResponseCurvesPrice), \
            'Error: obj_res must be a ResponseCurvesPrice object'
        self.res = obj_res
        self.y_pos = y_pos

        self.res.dic_req_param = {k: list(self.res.df_req[k].drop_duplicates())
                                  for k in self.res.dic_req_param}

        msg1 = 'Error: {} must be a column name in df_req'
        msg1b = 'Error: y_pos must be a "index" or "column"'
        msg2 = 'z must be None if y is None'
        msg3 = 'Error: dic_req_fix must be a dict'
        msg4 = 'Error: {} is not a column of df_req'
        msg5 = 'Error: {} has {} values - Must be one'
        msg6 = 'Error: value must be a column of df_res'
        msg7 = 'Error: {} is present in dic_req_fix'
        msg8 = 'Error: {} has {} values in dic_res_param - Must be one'

        assert x in self.res.df_req.columns, msg1.format('x')
        if y:
            assert y in self.res.df_req.columns, msg1.format('y')
            assert y_pos in ['index', 'column'], msg1b
        if x and y:
            if z is not None:
                assert z in self.res.df_req.columns, msg1.format('z')
        else:
            assert z is None, msg2

        assert isinstance(dic_req_fix, dict), msg3

        # transform
        for k, v in dic_req_fix.items():
            if isinstance(v, pd.Timestamp):
                v = Util.date_to_str(v)
                dic_req_fix[k] = v
            if isinstance(v, (str, int, float)):
                dic_req_fix[k] = [v]

        for k, v in dic_req_fix.items():
            assert k in self.res.df_req.columns, msg4.format(k)
            assert len(v) == 1, msg5.format(k, len(v))

        assert value in self.res.df_res.columns, msg6

        li_req_fix = list(dic_req_fix.keys())
        li_req_sel = copy.deepcopy(li_req_fix)
        li_xyz = [e for e in [x, y, z] if e is not None]
        for v in li_xyz:
            li_req_sel.append(v)
            assert v not in li_req_fix, msg7.format(v)
        # display(li_xyz)

        dic_req_param_full = copy.deepcopy(dic_req_fix)
        # display(dic_req_fix)
        dic_req_param_full = {k: v[0] for k, v in dic_req_param_full.items()}
        # display(dic_req_param_full)

        for c in self.res.df_req.columns:
            if c not in li_req_sel:
                v = self.res.dic_req_param[c]
                assert len(v) == 1, \
                    msg8.format(c, len(self.res.dic_res_param))
                dic_req_param_full[c] = v[0]

        # display(dic_req_param_full)
        li_mask = []
        for k, v in dic_req_param_full.items():
            # EXCEPTION
            if k != 'nominal':
                li_mask.append(self.res.df_req[k] == v)
        # display(li_mask)
        mask = functools.reduce((lambda x, y: x & y),
                                li_mask)

        df_slice = pd.concat([self.res.df_req[li_xyz],
                              self.res.df_res[value]], axis=1)
        # display(df_slice)
        df_slice = df_slice.loc[mask]
        self.df_slice = df_slice.reset_index(drop=True)

        self.df_pivot = None

        if len(li_xyz) == 1:
            df_pivot = df_slice[[x, value]]

            df_pivot = df_pivot.set_index(x)
            df_pivot = df_pivot.loc[self.res.dic_req_param[x]]

        if len(li_xyz) == 2:
            # display(df_slice)
            df_pivot = df_slice.pivot_table(index=x,
                                            columns=y,
                                            values=value)
            # display(df_pivot)
            df_pivot = df_pivot.loc[self.res.dic_req_param[x],
                                    self.res.dic_req_param[y]]

        if len(li_xyz) == 3:
            df_pivot = df_slice[[x, y, z, value]]

            if self.y_pos == 'index':
                df_pivot = df_pivot.pivot_table(index=[x, y],
                                                columns=z,
                                                values=value)

                df_pivot = df_pivot.reindex(self.res.dic_req_param[x],
                                            axis=0,
                                            level=0)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[y],
                                            axis=0,
                                            level=1)

                df_pivot = df_pivot.reindex(self.res.dic_req_param[z],
                                            axis=1)

            if self.y_pos == 'column':
                df_pivot = df_pivot.pivot_table(index=x,
                                                columns=[y, z],
                                                values=value)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[x],
                                            axis=0)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[y],
                                            axis=1,
                                            level=0)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[z],
                                            axis=1,
                                            level=1)

        self.df_pivot = df_pivot

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True,
             excel=False):
        """
        """
        if name is None:
            name = 'SG_Research_Rates'

        save_result(self.df_pivot,
                    folder_save, name=name + '_Components_response',
                    tagged=tagged,
                    excel=excel)

    def _repr_html_(self):
        """
        """
        return self.df_slice.to_html()