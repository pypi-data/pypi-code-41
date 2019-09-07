import http.client
import pandas as pd
from .config import Config


def get(dataset, **kwargs):
    """
    Return DataFrame of requested DecisionForest dataset.
    Args:
        dataset (str): Dataset codes are available on DecisionForest.com, example: dataset='SMD'
        ** date (str): Date, example: date='2018-12-28'
        ** start, end (str): Date filters, example: start='2018-12-28', end='2018-12-30'
        ** symbol (str): Symbol codes are available on DecisionForest.com on the product page , example: symbol='AAPL'
    """

    conn = http.client.HTTPSConnection(Config.DOMAIN)
    u = f"/api/{dataset}/?key={Config.KEY}"

    for key, value in kwargs.items():
        u = f'{u}&{key}={value}'

    conn.request("GET", u)
    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    data = eval(data)

    if dataset == 'SMD':
        d = {}
        for i in range(len(data)):
            d[i] = {}
            d[i]['date'] = data[i]['date']
            d[i]['symbol'] = data[i]['symbol']
            d[i]['sentiment'] = data[i]['sentiment']
            d[i]['probability'] = data[i]['probability']
            d[i]['ratio'] = data[i]['ratio']

        df = pd.DataFrame.from_dict(d, orient='index')
        df = df.sort_values(by=['date'])

    elif dataset == 'DFCF':
        d = {}
        for i in range(len(data)):
            d[i] = {}
            d[i]['date'] = data[i]['date']
            d[i]['symbol'] = data[i]['symbol']
            d[i]['intrinsic_value_per_share'] = float(
                data[i]['intrinsic_value_per_share'])
            d[i]['de'] = float(data[i]['de'])
            d[i]['cr'] = float(data[i]['cr'])
            d[i]['roe'] = float(data[i]['roe'])
            d[i]['close'] = float(data[i]['price'])
            d[i]['previous_close'] = float(data[i]['previous_close'])
            d[i]['move'] = float(data[i]['move'])

        df = pd.DataFrame.from_dict(d, orient='index')
        df = df.sort_values(by=['date'])
    
    elif dataset == 'DPRD':
        d = {}
        for i in range(len(data)):
            d[i] = {}
            d[i]['date'] = data[i]['date']
            d[i]['symbol'] = data[i]['symbol']
            d[i]['close_price'] = float(data[i]['close_price'])
            d[i]['p_class'] = float(data[i]['p_class'])
            d[i]['p_predict'] = float(data[i]['p_predict'])

        df = pd.DataFrame.from_dict(d, orient='index')
        df = df.sort_values(by=['date'])

    else:
        df = pd.DataFrame()

    return df
