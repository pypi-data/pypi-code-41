from sgmarkets_api_analytics_rates.endpoint import endpoint as ep
import pandas as pd

class MySwap():
    def __init__(self):
        self.start_date = None
        self.end_date= None
        self.issueDate= None
        self.maturityDate = None
        self.name = None
        self.Api = None
        self.fixedCoupon = None
        self.fixedFrequency = None
        self.rq = None
        self.fixedBasis = None
        self.fixedDiscountTicker = None
        self.floatingTicker = None
        self.floatingDiscountTicker = None
        self.daysToSettle = None
        self.notional = None
        self.type = None
        self.rq = None
        self.date = None
        self.name = None
        self.bday = True

    def _check_input_date_(self):
        if self.date is None:
            del self.date
        else:
            del self.start_date
            del self.end_date

    def _build_request_(self):
        self._check_input_date_()
        self.rq = ep.v1_swaps_price.request()
        for attr, v in self.__dict__.items():

            if attr in self.rq.leg_keys or attr in self.rq.__dict__.keys():
                setattr(self.rq, attr, v)

        self.rq.expand()

    def price(self):
        self._build_request_()
        res = self.rq.call_api(self.Api, debug = False)
        self.res = res.prices
        if 'R' in self.type.upper() and not 'P' in self.type.upper():
            sign = 1
        else:
            sign = -1
        res_sign = {}
        for r in self.res.columns:
            res_sign[r] = self.res[r]*sign
        self.swap_dic = res_sign
        self.price_df = pd.DataFrame(res_sign)


class MyPortfolio():
    def __init__(self):
        self.swaps = []
    def add(self,s):
        self.swaps.append(s)
    def delete(self,s):
        self.swaps.remove(s)
    def price(self):
        price = {}
        df = None
        for s in self.swaps:
            i = 1
            if s.name is None:
                n = 'Swap '+ str(i)
                i = i + 1
            else:
                n = s.name
            print('Pricing : ' + n)
            s.price()
            price[n] = s.price_df
            if df is None:
                df = s.price_df
            else:
                df = df + s.price_df
        self.all_price_dic = price
        self.all_price_df = pd.concat(price, axis =1)
        self.price_df = df
