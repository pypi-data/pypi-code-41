from sgmarkets_api_analytics_rates.endpoint import endpoint as ep
import pandas as pd
from IPython.display import display
import sgmarkets_api_analytics_data as SG
import sgmarkets_api_analytics_rates.biz as biz
import datetime

class Swap():
    def __init__(self):
        self.coupon = None
        self.forward = None
        self.tenor = None
        self.curve = None
        self.name = None
        self.Api = None
        self.start_date = None
        self.end_date = None
        self.ep = ep.v1_curves_price
        self.rq = None
        self.type = None
        self.notional = int(1e9)
        self.raw_date = None
        self.pv01 = None
        self.rates = None
        self.prices = None
        self.dv01 = None
        self.customSwapCurves = None
        self.convexity = None
        self.include_risks = False
        self.delta_ladder = None

    def _check_attributes_(self):
        list_c = ['EUR EURIBOR 6M', 'USD LIBOR 3M', 'GBP LIBOR 6M', 'JPY LIBOR 6M']
        assert isinstance(self.coupon, int) or isinstance(self.coupon,
                                                          float), "coupon: {} should be an int or a float".format(
            self.coupon)
        assert isinstance(self.notional, int) or isinstance(self.notional,
                                                            float), "coupon: {} should be an int or a float".format(
            self.notional)
        assert isinstance(self.forward, str), "forward: {} should be a string (YYYY-mm-dd) or '0m' for spot".format(
            self.forward)
        assert isinstance(self.tenor, str), "tenor: {} should be a string (YYYY-mm-dd)".format(self.tenor)
        assert self.curve in list_c, "curve: {} should be one of {}".format(self.curve, ','.join(list_c))
        assert isinstance(self.start_date, str), "start date: {} should be a string (YYYY-mm-dd)".format(
            self.start_date)
        assert isinstance(self.end_date, str), "end date: {} should be a string (YYYY-mm-dd)".format(self.end_date)
        assert self.type.upper() in ['PAYER', 'RECEIVER'], "type: {} should be either payer or reveiver".format(
            self.type)


    def _build_request_(self):
        self.rq = self.ep.request()
        self._check_attributes_()
        self.rq.start_date = self.start_date
        self.rq.end_date = self.end_date
        self.rq.all_combination = False
        self.rq.curve = self.curve
        self.rq.expiry = self.forward
        self.rq.tenor = self.tenor
        if self.customSwapCurves is not None:
            self.rq.customSwapCurves = self.customSwapCurves
        self.rq.expand()

    def _get_from_api_(self):
        self._build_request_()
        self.raw_data = self.rq.call_api(self.Api, debug=False)

    def _unpack_pv01_rates_(self):
        self.pv01 = self.ep.slice(self.raw_data, x='date', y='expiry', z='tenor', dic_req_fix={}, value='dv01',
                                  y_pos='column').df_pivot
        self.rates = self.ep.slice(self.raw_data, x='date', y='expiry', z='tenor', dic_req_fix={}, value='value',
                                   y_pos='column').df_pivot * 100

    def price(self):
        self._get_from_api_()
        self._unpack_pv01_rates_()
        if self.type.upper() == 'PAYER':
            self.prices = (self.rates - self.coupon) * self.pv01/100 * self.notional
            self.pv01 = - self.pv01 / 10000 * self.notional
        else:
            self.prices = (self.coupon - self.rates) * self.pv01/100 * self.notional
            self.pv01 = self.pv01 / 10000 * self.notional

        if self.include_risks:
            self.dv01_and_convexity()
        return self.prices

    def dv01_and_convexity(self):
        ra = RiskAnalysis()
        print(ra)
        ra.swap = self
        ra.dv01()
        ra.convexity()


class SwapPortfolio():
    def __init__(self):
        self.swaps = []
        self.rq = None
        self.ep = ep.v1_curves_price
        self.api = None
        self.prices = None
        self.names = None
        self.all_swap_prices = None
        self.all_swap_pv01 = None
        self.currency = 'EUR'
        self.curves = []
        self.include_risks = False
        self.pv01 = None
        self.dv01 = None
        self.convexity = None
        self.all_swap_convexity = None
        self.all_swap_dv01 = None

    def add(self, swap):
        self.swaps.append(swap)

    def remove(self, swap):
        self.swaps.remove(swap)

    def price(self, rename=False, update=False):
        self.names = []
        self.curves = []
        self.all_swap_prices = pd.DataFrame()
        self.all_swap_pv01 = pd.DataFrame()
        self.all_swap_convexity = pd.DataFrame()
        self.all_swap_dv01 = pd.DataFrame()
        for s in self.swaps:
            self.curves.append(s.curve)
            if s.name is not None:
                s.name = s.name
            else:
                s.name = s.curve[0:3] + ' ' + s.type +' '+ s.forward + ' ' + s.tenor
            if s.prices is None or update is True:
                if self.include_risks and s.convexity is None and s.include_risks is False:
                    display('pricing swap: {}'.format(s.name))
                    s.include_risks = True
                    s.price()
                else:
                    display('pricing swap: {}'.format(s.name))
                    s.price()
            self.names.append(s.name)
            ccy = self._get_exchange_rate_(s)
            price_in_currency = s.prices * ccy
            pv01_in_currency = s.pv01 * ccy
            self.all_swap_prices = pd.concat([self.all_swap_prices, price_in_currency.reindex(s.prices.index)], axis=1)
            self.all_swap_pv01 = pd.concat([self.all_swap_pv01, pv01_in_currency], axis=1)
            self.all_swap_prices.fillna(method='ffill', inplace=True)
            self.all_swap_pv01.fillna(method='ffill', inplace=True)

            if self.include_risks:
                dv01_in_currency = s.dv01 * ccy
                convexity_in_currency = s.convexity * ccy

                self.all_swap_convexity = pd.concat([self.all_swap_convexity, convexity_in_currency.reindex(s.prices.index)], axis=1)
                self.all_swap_dv01 = pd.concat([self.all_swap_dv01, dv01_in_currency.reindex(s.prices.index)], axis=1)
                self.all_swap_convexity.fillna(method='ffill', inplace=True)
                self.all_swap_dv01.fillna(method='ffill', inplace=True)

        if rename is True:
            self.rename_columns_with_swap_names()
        self.prices = self.all_swap_prices.sum(axis=1)
        self.pv01 = self.all_swap_pv01.sum(axis=1)
        if self.include_risks:
            self.dv01 = self.all_swap_dv01.sum(axis = 1)
            self.convexity = self.all_swap_convexity.sum(axis = 1)
        return self.prices


    def rename_columns_with_swap_names(self):
        self.all_swap_prices.columns = self.names
        self.all_swap_pv01.columns = self.names
        if self.include_risks:
            self.all_swap_convexity.columns = self.names
            self.all_swap_dv01.columns = self.names


    def _select_ccy_(self, cur):
        list_ccy = ['EURUSD', 'EURGBP', 'EURJPY', 'USDJPY', 'USDGBP', 'GBPJPY']
        if cur.upper() != self.currency:
            ccy = self.currency + cur.upper()
            op = 'div'
            if ccy not in list_ccy:
                ccy = cur.upper() + self.currency
                op = 'mult'
            assert ccy in list_ccy, "currency {} should be one of EUR, USD, GBP, JPY.".format(self.currency)
            return ccy, op
        else:
            return 1

    def _get_exchange_rate_(self, swap):
        if self._select_ccy_(swap.curve[0:3]) is not 1:
            ep_ = SG.endpoint.v2_quotes
            req = ep_.request()
            req.isins, op = self._select_ccy_(swap.curve[0:3])
            req.fields = 'RATE'
            req.startDate = list(swap.prices.index)[0].strftime('%Y-%m-%d')
            req.endDate = list(swap.prices.index)[-1].strftime('%Y-%m-%d')
            req.expand()
            display('Retrieving exchange rate {}'.format(req.isins))
            res = req.call_api(swap.Api, debug=False)
            res = res.res[req.isins[0]].fillna(method='ffill')
            if op is 'div':
                tmp = 1 / res
                tmp.columns = swap.prices.columns
                return tmp
            else:
                tmp = res
                tmp.columns = swap.prices.columns
                return tmp
        else:
            return 1


class RiskAnalysis():

    def __init__(self):
        self.swap = None
        self.shocks_up = None
        self.shocks_down = None
        self.swap_up = None
        self.swap_down = None
        self.sh = None
        self.curve = None
        self.dates = None

    def _make_requests_(self):
        self.swap_up = Swap()
        self.swap_down = Swap()
        attr = ['Api','coupon','curve','end_date','start_date','tenor','forward','notional','type']
        for a in attr:

            setattr(self.swap_up,a, getattr(self.swap,a))
            setattr(self.swap_down,a, getattr(self.swap,a))

        self.swap_up.customSwapCurves = self.shocks_up
        self.swap_down.customSwapCurves = self.shocks_down
        self.swap_up.price()
        self.swap_down.price()

    def price(self):
        self._make_requests()

    def dv01(self,sh=1):
        self.sh = sh
        tenor = ['1M','3M','6M','9M'] + biz.build_tenors('1Y','60Y','1Y')
        shocks_up = biz.build_parralel_shocks(tenor,'@'+str(sh)+'bp')
        shocks_down = biz.build_parralel_shocks(tenor,'@-'+str(sh)+'bp')
        if self.dates is None:
            self.dates = [d.strftime('%Y-%m-%d') for d in self.swap.prices.dropna().index]
        if self.swap.curve == 'USD LIBOR 3M':
            self.curve = 'USD LIBOR 3M SBB UNADJ.'
        elif self.swap.curve == 'GBP LIBOR 6M':
            self.curve = 'GBP LIBOR 6M SMM'
        else:
            self.curve = self.swap.curve
        self.shocks_up = biz.generate_curve_shocks(self.dates, self.curve, shocks_up)
        self.shocks_down = biz.generate_curve_shocks(self.dates, self.curve, shocks_down)
        self._make_requests_()
        self.swap.dv01 = (self.swap_down.prices - self.swap_up.prices)/2 * 1/sh

        return self.swap.dv01

    def convexity(self):
        if self.swap_up.prices is None:
            self._make_requests_()
        self.swap.convexity = (self.swap_down.prices + self.swap_up.prices - 2 * self.swap.prices.dropna().reindex(self.dates))/(self.sh/100**2)/10000 *1/self.sh
        return self.swap.convexity


class Bump():
    def __init__(self):
        self.swap = None
        self.swap_shocked = None
        self.curve = None
        self.dates = None
        self.method = 'full'
        self.shocks = None
        self.bump_prices = {}
        self.shock = '@1bp'
        self.all_tenors = None

    def _check_and_create_couples(self):

        if self.swap.curve == 'USD LIBOR 3M':
            self.curve = 'USD LIBOR 3M SBB UNADJ.'
        elif self.swap.curve == 'GBP LIBOR 6M':
            self.curve = 'GBP LIBOR 6M SMM'
        else:
            self.curve = self.swap.curve

        assert self.method.lower() in ['full', 'bucket'], 'method should be one of full or bucket. Here {}'.format(
            self.method)
        if self.shocks is None:
            self.couples, self.all_tenors = biz._create_couples(self.method, self.shock)
        else:
            assert isinstance(self.shocks, dict), 'shocks should be a dict. Here: {}'.format(type(self.shocks))
            assert 'tenor' in self.shocks.keys() and 'shock' in self.shocks.keys(), 'tenor and shock should be shocks dict keys. Here {}'.format(
                self.shocks.keys())
            self.couples, self.all_tenors = biz._create_couples(self.method, self.shock, kwargs=self.shocks)

    def _make_requests_(self):
        self._check_and_create_couples()
        self.swap_shocked = Swap()
        attr = ['Api', 'coupon', 'curve', 'end_date', 'start_date', 'tenor', 'forward', 'notional', 'type']
        for a in attr:
            setattr(self.swap_shocked, a, getattr(self.swap, a))
        if self.dates is None:
            self.dates = [d.strftime('%Y-%m-%d') for d in self.swap.prices.dropna().index]
            # print(self.couples)
        for c in self.couples:
            if isinstance(c[0], list):
                n = c[0][-1]
                print(c)
                remove = [x for x in self.all_tenors if x not in c[0]]
                sh = {**biz.build_parralel_shocks(c[0], c[1]), **biz.build_parralel_shocks(remove, '@0bp')}
                self.swap_shocked.customSwapCurves = biz.generate_curve_shocks(self.dates, self.curve,
                                                                               sh)
                # print(self.swap_shocked.customSwapCurves)
            else:
                print(c)
                remove = [x for x in self.all_tenors if x not in [c[0]]]
                sh = {**biz.build_parralel_shocks([c[0]], c[1]), **biz.build_parralel_shocks(remove, '@0bp')}
                self.swap_shocked.customSwapCurves = biz.generate_curve_shocks(self.dates, self.curve,
                                                                               sh)

                n = c[0]


                # print(self.swap_shocked.customSwapCurves)

            self.bump_prices[n] = self.swap_shocked.price()

    def apply_bump(self):
        self._make_requests_()


class DeltaLadder():
    def __init__(self):
        self.swap = None
        self.swap_delta_ladder = {}
        self.dates = None
        self.method = 'full'
        self.shocks = None
        self.shocks_up = None
        self.shocks_down = None
        self.bump_up = None
        self.bump_down = None
        self.shock_up = 1
        self.shock_down = None
        self.shock = 1
        self.type = 'one side'
        self.bump = None

    def _compute_two_sided(self):
        attr = ['swap', 'dates', 'method']
        self.bump_up = Bump()
        self.bump_down = Bump()
        for a in attr:
            setattr(self.bump_up, a, getattr(self, a))
            setattr(self.bump_down, a, getattr(self, a))
        if self.shocks_up is not None and self.shocks_down is None:
            self.shocks_down = {'tenor': self.shocks_up['tenor'],
                                'shock': ['@-' + s.replace('@', '').replace('bp', '') + 'bp'
                                          for s in self.shocks_up['shock']]}
        elif self.shocks_down is not None and self.shocks_down is None:
            self.shocks_up = {'tenor': self.shocks_down['tenor'],
                              'shock': ['@' + s.replace('@-', '').replace('bp', '') + 'bp'
                                        for s in self.shocks_down['shock']]}
        if self.shock_up is not None and self.shock_down is None:

            self.bump_up.shock = '@' + str(self.shock_up) + 'bp'
            self.bump_down.shock = '@-' + str(self.shock_up) + 'bp'
        else:
            self.bump_up.shock = '@' + str(self.shock_up) + 'bp'
            self.bump_down.shock = '@' + str(self.shock_down) + 'bp'

        self.bump_up.shocks = self.shocks_up
        self.bump_down.shocks = self.shocks_down

        self.bump_up.apply_bump()
        self.bump_down.apply_bump()

    def _compute_one_sided(self):
        attr = ['swap', 'dates', 'method', 'shocks']
        self.bump = Bump()

        for a in attr:
            setattr(self.bump, a, getattr(self, a))

        self.bump.shock = '@' + str(self.shock) + 'bp'

        self.bump.apply_bump()

    def get_ladder(self):
        if self.type.lower() == 'one side':
            self._compute_one_sided()
            for k, v in self.bump.bump_prices.items():
                self.swap_delta_ladder[k] = self.swap.prices - v
        if self.type.lower() == 'two side':
            self._compute_two_sided()
            for k, v in self.bump_up.bump_prices.items():
                self.swap_delta_ladder[k] = (self.bump_down.bump_prices[k] - v) / 2 * 1 / self.shock_up
        self.swap.delta_ladder = pd.concat(self.swap_delta_ladder, axis = 1)


