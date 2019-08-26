from sgmarkets_api_analytics_rates._obj_from_dict import ObjFromDict
from sgmarkets_api_analytics_rates.request_curves_price import RequestCurvesPrices
from sgmarkets_api_analytics_rates.response_curves_price import ResponseCurvesPrice
from sgmarkets_api_analytics_rates.slice_curves_price import SliceCurvesPrice
from sgmarkets_api_analytics_rates.request_curves_custom import RequestCurvesCustom
from sgmarkets_api_analytics_rates.request_swaps_price import RequestSwapsPrice
from sgmarkets_api_analytics_rates.response_swaps_price import ResponseSwapsPrice
dic_endpoint = {
    'v1_curves_price': {
        'request': RequestCurvesPrices,
        'response': ResponseCurvesPrice,
        'slice': SliceCurvesPrice
    },
    'v1_custom_prices': {
        'request': RequestCurvesCustom,
        'response': ResponseCurvesPrice,
        'slice': SliceCurvesPrice
    },
    'v1_swaps_price':{
        'request': RequestSwapsPrice,
        'response': ResponseSwapsPrice,
        #'slice': SliceSwapsPrice,
    },

}

endpoint = ObjFromDict(dic_endpoint)

if __name__ == '__main__':
    from sgmarkets_api_auth import Api
    from sgmarkets_api_analytics_rates import biz
    from sgmarkets_api_analytics_rates.biz import swap

    ep = endpoint
    rq = ep.v1_swaps_price.request()
    rq.date = ['2019-08-22']
    #rq.start_date = "2017-06-07"
    #rq.end_date = '2017-07-24'
    rq.issueDate = "2017-06-05"
    rq.maturityDate = "2033-02-25"
    rq.fixedCoupon =  "0.01"
    rq.fixedFrequency =  "1Y"
    rq.fixedBasis = "30/360U"
    rq.fixedDiscountTicker =  "EONIA"
    rq.floatingTicker = "EUR EURIBOR 6M"
    rq.floatingDiscountTicker =  "EONIA"
    rq.daysToSettle =  0
    rq.notional = 10000000
    rq.expand()
    a = Api()
    res = rq.call_api(a, debug=True)

    print(res.prices.columns)
   # from sgmarkets_api_auth import Api


    s2 = swap.MySwap()
    #s.date = ['2019-08-21']
    s2.start_date = "2018-06-05"
    s2.end_date = '2019-08-22'
    s2.issueDate = "2017-06-05"
    s2.maturityDate = "2033-02-25"
    s2.fixedCoupon = "0.01"
    s2.fixedFrequency =  "1Y"
    s2.fixedBasis = "30/360U"
    s2.fixedDiscountTicker =  "EONIA"
    s2.floatingTicker = "EUR EURIBOR 6M"
    s2.floatingDiscountTicker =  "EONIA"
    s2.daysToSettle = 2
    s2.notional = 10000000
    s2.type = 'payer'
    s2.Api = Api()
    s2.name = 'MySwap2'


    #s.price()
    #print(s.swap_df)
    # a = Api()
    s = swap.MySwap()
    s.start_date = "2017-06-05"
    s.end_date = '2019-08-22'
    s.issueDate = "2017-06-05"
    s.maturityDate = "2033-02-25"
    s.fixedCoupon = "0.03"
    s.fixedFrequency =  "1Y"
    s.fixedBasis = "30/360U"
    s.fixedDiscountTicker =  "EONIA"
    s.floatingTicker = "EUR EURIBOR 6M"
    s.floatingDiscountTicker =  "EONIA"
    s.daysToSettle = 2
    s.notional = 10000000
    s.type = 'receiver'
    s.Api = Api()
    s.name = 'MySwap'
    port = swap.MyPortfolio()
    port.add(s)
    port.add(s2)
    port.price()
    print(port.all_price_df)
    print(port.price_df)