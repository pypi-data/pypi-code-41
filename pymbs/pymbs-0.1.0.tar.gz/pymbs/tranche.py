"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.

Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

from collections import OrderedDict
import decimal

import pandas as pd

from pymbs.log import get_logger

logger = get_logger(__name__)

dec = decimal.Decimal
d0 = dec('0')
d1200 = dec('1200')
cleanup = dec('1E-2')

# TODO: Get the initial rate from the model and get the subsequent rates
# from a FRED lookup
LIBOR = 1.31


class Tranche(object):
    """The Tranche object represents a tranche in the deal.
    It is used to store all pertinent information about the tranche,
    including any cash flows calculated for it.

    The current design of this object provides an experimental 'child tranche'
    option, which allows for the creation of pseudo tranches, to enable a
    true tree-like representation of the cash flow structure and the payment
    waterfall.

    Generally speaking, when reversing a deal, the cash flow structure is
    flattened so that only the tranches disclosed in the Prospectus Supplement
    are included in the model.

    The tree representation with its attending pseudo tranches offeres a truer
    rendition of the model, but may not be necessary and requires a greater
    understanding of structured cash flow models. This functionality *may*
    be deprecated and removed in future releases.
    """

    def __init__(
        self, group, id, upb, coupon, floater_formula, floater_cap,
        floater_floor, prin_type, int_type, notional_with, delay, retail, macr,
        final_payment_date, cusip, schedule,
        dated_date=None, next_payment_date=None
    ):
        self._assumed_price = dec('1.00')
        self._cash_flows = {}
        self._child_tranches = []
        self._coupon = coupon
        self._cusip = cusip
        self._dated_date = dated_date
        self._delay = delay
        self._final_payment_date = final_payment_date
        self._floater_cap = floater_cap
        self._floater_floor = floater_floor
        self._floater_formula = floater_formula
        self._group = group
        self._id = id
        self._int_type = int_type
        self._macr = macr
        self._next_payment_date = next_payment_date
        self._notional_with = notional_with
        self._original_upb = upb
        self._periodic_cf = OrderedDict()
        self._periodic_prepay_scenario = ''
        self._price_at_issuance = dec('1.00')
        self._prin_type = prin_type
        self._pro_rated_ratio = dec('0')
        self._retail = retail
        self._schedule = schedule
        self._strips = []
        self._upb = upb

    @property
    def assumed_price(self):
        return self._assumed_price

    @assumed_price.setter
    def assumed_price(self, value):
        self._assumed_price = value

    @property
    def cash_flows(self):
        return self._cash_flows

    @property
    def child_tranches(self):
        return self._child_tranches

    @property
    def coupon(self):
        return self._coupon

    @coupon.setter
    def coupon(self, value):
        self._coupon = value

    @property
    def cusip(self):
        return self._cusip

    @cusip.setter
    def cusip(self, value):
        self._cusip = value

    @property
    def dated_date(self):
        return self._dated_date

    @dated_date.setter
    def dated_date(self, value):
        self._dated_date = value

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value

    @property
    def final_payment_date(self):
        return self._final_payment_date

    @final_payment_date.setter
    def final_payment_date(self, value):
        self._final_payment_date = value

    @property
    def floater_cap(self):
        return self._floater_cap

    @floater_cap.setter
    def floater_cap(self, value):
        self._floater_cap = value

    @property
    def floater_floor(self):
        return self._floater_floor

    @floater_floor.setter
    def floater_floor(self, value):
        self._floater_floor = value

    @property
    def floater_formula(self):
        return self._floater_formula

    @floater_formula.setter
    def floater_formula(self, value):
        self._floater_formula = value

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._floater_floor = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._floater_floor = value

    @property
    def int_type(self):
        return self._int_type

    @int_type.setter
    def int_type(self, value):
        self._int_type = value

    @property
    def macr(self):
        return self._macr

    @macr.setter
    def macr(self, value):
        self._macr = value

    @property
    def next_payment_date(self):
        return self._next_payment_date

    @next_payment_date.setter
    def next_payment_date(self, value):
        self._next_payment_date = value

    @property
    def notional_with(self):
        return self._notional_with

    @notional_with.setter
    def notional_with(self, value):
        self._notional_with.clear()
        self._notional_with.extend(value)

    @property
    def original_upb(self):
        return self._original_upb

    @original_upb.setter
    def original_upb(self, value):
        self._original_upb = value

    @property
    def periodic_cf(self):
        return self._periodic_cf

    @periodic_cf.setter
    def periodic_cf(self, value):
        self._periodic_cf = value

    @property
    def periodic_prepay_scenario(self):
        return self._periodic_prepay_scenario

    @periodic_prepay_scenario.setter
    def periodic_prepay_scenario(self, value):
        self._periodic_prepay_scenario = value

    @property
    def price_at_issuance(self):
        return self._price_at_issuance

    @price_at_issuance.setter
    def price_at_issuance(self, value):
        self._price_at_issuance = dec(value)

    @property
    def prin_type(self):
        return self._prin_type

    @prin_type.setter
    def prin_type(self, value):
        self._prin_type = value

    @property
    def pro_rated_ratio(self):
        return self._pro_rated_ratio

    @pro_rated_ratio.setter
    def pro_rated_ratio(self, value):
        self._pro_rated_ratio = dec(value)

    @property
    def retail(self):
        return self._retail

    @retail.setter
    def retail(self, value):
        self._retail = value

    @property
    def schedule(self):
        return self._schedule

    @schedule.setter
    def schedule(self, value):
        self._schedule = value

    @property
    def strips(self):
        """This is a list of Notional tranches, whose interest was stripped
        from this tranche. It is the corollary to the 'notional_with'
        attribute.

        TODO: Need to actually populate this list during the loading of the
        model!
        """
        return self._strips

    @strips.setter
    def strips(self, value):
        self._strips.append(value)

    @property
    def upb(self):
        return self._upb

    @upb.setter
    def upb(self, value):
        self._upb = value

    def new_child_tranche(
        self, group, id, upb, coupon, floater_formula, floater_cap,
        floater_floor, prin_type, int_type, notional_with, delay, retail, macr,
        final_payment_date, cusip, schedule,
        dated_date=None, next_payment_date=None
    ):
        tranche = Tranche(
            group, id, upb, coupon, floater_formula, floater_cap,
            floater_floor, prin_type, int_type, notional_with, delay, retail,
            macr, final_payment_date, cusip, schedule,
            dated_date=None, next_payment_date=None
        )
        self.child_tranches.append(tranche)

        return tranche

    def end_periodic_cf(self):
        self.cash_flows[self.periodic_prepay_scenario].append(
            self.periodic_cf.copy()
        )

    def new_periodic_cf(self, prepay_scenario, period, payment_date):
        if prepay_scenario != self.periodic_prepay_scenario:
            self.periodic_prepay_scenario = prepay_scenario
            self.cash_flows[self.periodic_prepay_scenario] = []
            self.upb = self.original_upb
        self.periodic_cf.clear()
        self._initialize_periodic_flow(period, payment_date)

    def _initialize_periodic_flow(self, period, payment_date):
        self.periodic_cf = OrderedDict().fromkeys(
            [
                'period',
                'payment_date',
                'beginning_balance',
                'interest',
                'accrual',
                'principal',
                'ending_balance'
            ]
        )
        self.periodic_cf['period'] = period
        self.periodic_cf['payment_date'] = payment_date
        self.periodic_cf['beginning_balance'] = self.upb
        self.periodic_cf['interest'] = dec('0')
        self.periodic_cf['accrual'] = dec('0')
        self.periodic_cf['principal'] = dec('0')
        self.periodic_cf['ending_balance'] = self.upb

    def pay_accrue(self):
        self.periodic_cf['accrual'] += self.periodic_cf['interest']
        self.periodic_cf['ending_balance'] += self.periodic_cf['accrual']
        self.upb += self.periodic_cf['accrual']
        self.periodic_cf['interest'] = dec('0')

    def pay_interest(self, collat_net_interest):
        balance = self.upb
        if self.floater_formula:
            coupon = min(
                max(dec(eval(self.floater_formula)), self.floater_floor),
                self.floater_cap
            )
        else:
            coupon = self.coupon
        interest_payment = balance * (coupon / d1200)
        self.periodic_cf['interest'] = interest_payment
        collat_net_interest -= interest_payment

        return collat_net_interest

    def pay_principal(self, principal_payment):
        self.upb -= principal_payment
        if self.upb <= cleanup:
            self.upb = d0
        self.periodic_cf['principal'] += principal_payment
        self.periodic_cf['ending_balance'] -= principal_payment

    def reduce_notional_balance(self):
        pass

    def tabulate_cf(self):
        for prepay_scenario in self.cash_flows:
            cash_flow_table = pd.DataFrame.from_dict(
                self.cash_flows[prepay_scenario]
            )
            self.cash_flows[prepay_scenario] = cash_flow_table


class IndexRate(object):
    """Create and Index rate object for each Benchmark Index used in the deal.

    Traditionally, the most popular index for Mortgage-Backed Securites has
    been 1-Month LIBOR (The London Inter-bank Offered Rate).
    However, in light of recent revelations reagrding LIBOR-fixing
    by market makers, it is being phased-out, in favor of SOFR -
    the Secured Overnight Financing Rate.

    Other Index Rate Benchmarks may be used as well.
    """

    def __init__(self, name, benchmark, fred_ticker, initial_rate):
        self._name = name
        self._benchmark = benchmark
        self._fred_ticker = fred_ticker
        self._initial_rate = initial_rate

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def benchmark(self):
        return self._benchmark

    @benchmark.setter
    def benchmark(self, value):
        self._benchmark = value

    @property
    def fred_ticker(self):
        return self._fred_ticker

    @fred_ticker.setter
    def fred_ticker(self, value):
        self._fred_ticker = value

    @property
    def initial_rate(self):
        return self._initial_rate

    @initial_rate.setter
    def initial_rate(self, value):
        self._initial_rate = value
