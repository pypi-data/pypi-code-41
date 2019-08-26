import numpy as np
import pandas as pd
from itertools import product
from itertools import combinations

ROUND_NB_DIGIT = 2


def get_diff(data, start_date, end_date):
    """
    get difference between 2 dates
    """
    mask_1 = (data.index.get_level_values('date') == end_date)
    mask_2 = (data.index.get_level_values('date') == start_date)
    one = data.loc[mask_1]
    one.index = one.index.droplevel('date')
    two = data.loc[mask_2]
    two.index = two.index.droplevel('date')
    # res=res.index.droplevel('date')
    return one - two


def get_max(data, resize=False, *args):
    """
    get max
    TBC
    """
    if resize:
        data = select_data(data, *args)
    x = data.groupby(level='expiry').apply(max)
    return x.reindex(data.index.get_level_values('expiry').unique(), axis=0)


def get_min(data, resize=False, *args):
    """
    get min
    TBC
    """
    if resize:
        data = select_data(data, *args)
    x = data.groupby(level='expiry').apply(min)
    return x.reindex(data.index.get_level_values('expiry').unique(), axis=0)


def get_surface(data, date):
    """
    get surface for given date
    TBC
    """
    mask = (data.index.get_level_values('date') == date)
    x = data.loc[mask]
    return drop_level(x, 'date')


def select_data(data, args):
    """
    select data from dataframe
    args:
        for discrete values
            field, value1, value2, etc
        for range of values
            field, value_start, value_end, 'range'

    returns subset dataframe
    TBC
    """
    arg = args
    if arg[0] == 'date':
        if len(arg) == 4 and arg[3] == 'range':
            mask = (data.index.get_level_values(arg[0]) >= arg[1]) & (
                data.index.get_level_values(arg[0]) <= arg[2])
        else:
            mask = (data.index.get_level_values(arg[0]) == arg[1])
            for ar in arg[2:len(arg)]:
                mask = mask | (data.index.get_level_values(arg[0]) == ar)
    else:
        mask = (data.index.get_level_values(arg[0]) == arg[1])
        for ar in arg[2:len(arg)]:
            mask = mask | (data.index.get_level_values(arg[0]) == ar)

    return data.loc[mask]


def drop_level(data, index):
    """
    drop level of input dataframe - inplace
    TBC
    """
    data.index = data.index.droplevel(index)
    return data


def get_percentile(data, date, resize=False, *args):
    """
    get percentile rank from input dataframe
    TBC
    """
    if resize:
        data = select_data(data, *args)
    return get_surface(data.groupby(level='expiry').rank(pct=True), date)


def get_mean(data, resize=False, *args):
    """
    get mean
    TBC
    """
    if resize:
        data = select_data(data, *args)
    data = data.dropna()
    x = data.groupby(level='expiry').apply(np.mean)
    return x.reindex(data.index.get_level_values('expiry').unique(), axis=0)


def get_std(data, resize=False, *args):
    """
    get standard deviation
    TBC
    """
    if resize:
        data = select_data(data, *args)
    data = data.dropna()
    x = data.groupby(level='expiry').apply(np.std)
    return x.reindex(data.index.get_level_values('expiry').unique(), axis=0)


def get_z_score(data, end_dt, resize=False, *args):
    """
    get z-score
    TBC
    """
    if resize:
        data = select_data(data, *args)
    return (get_surface(data, end_dt) - get_mean(data)) / get_std(data)


def build_weight(spread, weight, **kwargs):
    """
    build weight
    TBC
    """
    if (len(spread) is not len(weight)):
        if kwargs == {}:
            kwargs.setdefault('type', 'S')
        else:
            kwargs = kwargs['kwargs']

        if (len(spread) % 2 == 0 or (len(spread) % 2 == 0 and len(spread) % 3 == 0)) and (kwargs['type'].upper() != 'FLY' or kwargs['type'].upper() != 'F'):
            print('spread - weight len mismatch by default spread weighted (-1,1)')
            w = np.repeat(1, len(spread))
            pos = np.arange(1, len(w), 2)
            w[pos] = w[pos] * -1
        elif (len(spread) % 3 == 0 or (len(spread) % 2 == 0 and len(spread) % 3 == 0)) and (kwargs['type'].upper() == 'FLY' or kwargs['type'].upper() == 'F'):
            print('fly - weight len mismatch by default fly weighted (-1,2,-1)')
            w = np.repeat(-1, len(spread))
            pos = np.arange(1, len(w), 2)
            w[pos] = w[pos] * -2
    else:
        w = weight
    return w

# def build_spread(data, spread, typ_, resize=False, *args):
#     """
#     build spread
#     TBC
#     """
#     if resize:
#         data = select_data(data, args)
#     res = pd.DataFrame()
#     if typ_.upper() == "S" or typ_.upper() == "SLOPE":
#         for s in spread:
#             res[s[0] + s[1]] = data[s[1]] - data[s[0]]
#         return res
#     if typ_.upper() == "C" or typ._upper() == "CALENDAR":
#         from collections import OrderedDict
#         dic = OrderedDict()
#         for s in spread:
#             dic[(s[0] + s[1])] = data.loc[s[1]] - data.loc[s[0]]
#         res = pd.concat(dic.values(), keys=dic.keys())
#         res.index.names = ('expiry', 'date')
#         return res


def build_spread(data, spread, axis="T", weight=[], resize=False, *args, **kwargs):
    """
    build weight
    TBC
    """
    if resize:
        data = select_data(data, args)
    res = pd.DataFrame()
    w = build_weight(spread[0], weight, **kwargs)
    if axis.upper() == 'T' or axis.upper() == 'TENOR':
        for s in spread:
            nme = str()
            for i, e in enumerate(s):
                if i == 0:
                    res_tmp = data[s[i]] * w[i]
                else:
                    res_tmp = res_tmp + data[s[i]] * w[i]
                nme = nme + s[i]
            res[nme] = res_tmp
        return res

    if axis.upper() == 'E' or axis.upper() == 'EXPIRY':
        from collections import OrderedDict
        dic = OrderedDict()
        idx = data.loc[spread[0][0]].index
        col = data.loc[spread[0][0]].columns
        for s in spread:
            res_tmp = pd.DataFrame(0, index=idx, columns=col)
            nme = str()
            for i, e in enumerate(s):
                res_tmp = res_tmp + data.loc[s[i]] * w[i]
                nme = nme + s[i]
            dic[nme] = res_tmp
        res = pd.concat(dic.values(), keys=dic.keys())
        res.index.names = ('expiry', 'date')
        return res

def swap_prices(rates, dv01, nominal = int(1e6), w=None, hedge='None'):
    if w is None:
        w2 = [1]*len(rates.columns)
    else:
        w2 = []
        for ww in w:
            if isinstance(ww, str):
                if ww.upper() == 'PAYER' or ww.upper() == 'P':
                    w2.append(1)
                elif ww.upper() == 'RECEIVER' or ww.upper() == 'R':
                    w2.append(-1)
            else:
                w2.append(ww)

    if hedge.upper() == 'DV01':

        w_ = [1/(dv01.iloc[0,i]/dv01.iloc[0, 0]) for i in range(len(dv01.columns))]
        w2 = [a*b for a,b in zip(w_, w2)]

    ret = rates.diff(1).fillna(0)
    prices = ret * dv01 * w2 * nominal
    prices.columns = [str(w[c]) +' '+ list(prices.columns)[c][0]+' '+list(prices.columns)[c][1] for c in range(len(prices.columns))]
    portfolio_price = prices.sum(axis=1)
    res = pd.concat([prices, portfolio_price], axis = 1)
    res.columns = list(prices.columns) + ['strategy price']
    for c in prices.columns:
        res[c + ' PnL'] = prices[c].cumsum()
    res['strategy PnL'] = res['strategy price'].cumsum()
    return w2, res


def build_rolldown(couples, period):
    cpl = []
    ten = []
    exp = []
    if 'y' in period:
        period = int(period.replace('y', '')) * 12
    else:
        period = int(period.replace('m', ''))
    for l in couples:
        exp.append(l[0])
        ten.append(l[1])
        if 'y' in l[0]:
            e = int(l[0].replace('y', '')) * 12
        else:
            e = int(l[0].replace('m', ''))

        if 'y' in l[1]:
            t = int(l[1].replace('y', '')) * 12
        else:
            t = int(l[1].replace('m', ''))

        diff = e - period
        if diff >= 0:
            if diff % 12 == 0 and diff != 0:
                e = str(int(diff / 12)) + 'y'
            else:
                e = str(int(diff)) + 'm'
            if t % 12 == 0:
                t = str(int(t / 12)) + 'y'
            else:
                t = str(int(t)) + 'm'
            exp.append(e)
            ten.append(t)
            cpl.append(((e, t), l))

        else:
            exp.append('0m')
            diff_t = t + diff
            if diff_t % 12 == 0:
                t = str(int(diff_t / 12)) + 'y'
            else:
                t = str(int(diff_t)) + 'm'
            ten.append(t)
            cpl.append((('0m', t), l))

    return ','.join(list(set(exp))), ','.join(list(set(ten))), cpl


def build_couples(exp,ten):
    return [(e,t) for e, t in product(exp,ten)]

def rolldown(df, cpl, w=None):
        if not w:
            w = [-1, 1]
        res = {}
        for c in cpl:
            d = w[0] * df[c[0][1]].loc[c[0][0]] + w[1] * df[c[1][1]].loc[c[1][0]]
            d = pd.DataFrame(d)
            d.columns = [c[1][1]]
            if not c[1][0] in res.keys():
                res[c[1][0]] = d
            else:
                res[c[1][0]] = pd.concat([res[c[1][0]], d], axis=1)
        return pd.concat(res)


def spread_cross(df, cpl, w=None):
    if not w:
        w = [-1, 1]
    res = pd.DataFrame()
    for c in cpl:
        res[c[1][0] + c[1][1] + '-' + c[0][0] + c[0][1]] = w[0] * df[c[0][1]].loc[c[0][0]] + w[1] * df[c[1][1]].loc[
            c[1][0]]
    return res


def build_tenor_rolldown_spot(list_of_tenor, period):
    if not isinstance(list_of_tenor, list):
        list_of_tenor = list_of_tenor.split(',')
    ten = []
    for l in list_of_tenor:
        if 'y' in l:
            n = int(l.replace('y', '')) * 12 - period
            assert n >= 0, 'period should be inferior or equal to the shortest expiries'
            ten.append(str(n) + 'm')
        else:
            n = int(l.replace('m', '')) - period
            assert n >= 0, 'period should be inferior or equal to the shortest expiries'
            ten.append(str(n) + 'm')
    new_ten = list_of_tenor + ten

    return ','.join(new_ten), [(ten[i], list_of_tenor[i]) for i in range(len(ten))]


def build_carry(couples, period):
    cpl = []
    ten = []
    exp = []
    if 'y' in period:
        period = int(period.replace('y', '')) * 12
    else:
        period = int(period.replace('m', ''))
    for l in couples:
        exp.append(l[0])
        ten.append(l[1])
        if 'y' in l[0]:
            e = int(l[0].replace('y', '')) * 12
        else:
            e = int(l[0].replace('m', ''))

        if 'y' in l[1]:
            t = int(l[1].replace('y', '')) * 12
        else:
            t = int(l[1].replace('m', ''))

        diff_exp = period - e
        if diff_exp <= 0:
            exp.append(l[0])
            ten.append(l[1])
            e_ = l[0]
            t = l[1]
            l_2 = l

        else:
            e = period - e
            if e % 12 == 0:
                e_ = str(int(e / 12)) + 'y'
            else:
                e_ = str(int(e)) + 'm'
            exp.append(e_)
            t = t - e
            if t % 12 == 0:
                t = str(int(t / 12)) + 'y'
            else:
                t = str(int(t)) + 'm'
            ten.append(t)
            l_2 = l
            l = ('0m', l[1])
        cpl.append(((e_, t), l, l_2))

    return ','.join(list(set(exp))), ','.join(list(set(ten))), cpl


def carry_approximation(df, cpl, w=None):
    if not w:
        w = [1, -1]
    res = {}
    for c in cpl:
        d = w[0] * df[c[0][1]].loc[c[0][0]] + w[1] * df[c[1][1]].loc[c[1][0]]
        d = pd.DataFrame(d)
        d.columns = [c[2][1]]
        if not c[2][0] in res.keys():
            res[c[2][0]] = d
        else:
            res[c[2][0]] = pd.concat([res[c[2][0]], d], axis=1)
    return pd.concat(res)

def generate_curve_shocks(dates, curve, ten_shock):
    return {d: {curve:{'curve': [{'tenor':t,'value':s} for t,s in ten_shock.items()]}} for d in dates}

def build_parralel_shocks(tenors,shock):
    return {t: shock for t in tenors}



def build_tenors(start, end, step):
    if 'M' in start.upper() and 'M' in end.upper():
        start = int(start.replace('M', ''))
        end = int(end.replace('M', ''))
        t = 'M'
    elif 'Y' in start.upper() and 'Y' in end.upper():
        start = int(start.replace('Y', ''))
        end = int(end.replace('Y', ''))
        t = 'Y'
    elif 'M' in start.upper() and 'Y' in end.upper():
        start = int(start.replace('M', ''))
        end = int(end.replace('Y', '')) * 12
        t = 'M'
    else:
        return 'error'
    if t in step:
        step = int(step.replace(t, ''))
    elif 'M' in step and t is 'Y':
        step = int(step.replace('M', '')) / 12
    else:
        return 'error'
    res = np.arange(start, end + step, step)

    return [str(r) + t for r in res]


def _create_couples(method='full', s='@1bp', **kwargs):
    if method.lower() == 'full':
        if not kwargs:
            tenor = ['1M', '3M', '6M', '9M'] + build_tenors('1Y', '100Y', '1Y')
            shock = [s] * len(tenor)
            ten = tenor
        else:
            tenor = kwargs['kwargs']['tenor']
            shock = kwargs['kwargs']['shock']
            ten = tenor
    elif method.lower() == 'bucket':
        if not kwargs:
            tenor = [['1M', '3M', '6M', '9M', '12M', '18M', '2Y'], build_tenors('3Y', '5Y', '1Y'),
                     build_tenors('6Y', '10Y', '1Y')
                , build_tenors('11Y', '20Y', '1Y'), build_tenors('21Y', '30Y', '1Y')
                , build_tenors('31Y', '50Y', '1Y'), build_tenors('51Y', '100Y', '1Y')]

            shock = [s] * sum([len(t) for t in tenor])
            ten = [item for sublist in tenor for item in sublist]
        else:
            tenor = kwargs['kwargs']['tenor']
            shock = kwargs['kwargs']['shock']
            ten = [item for sublist in tenor for item in sublist]

    couples = zip(tenor, shock)
    return list(couples), ten