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
    understanfding of structured cash flow models. This functionality *may*
    be deprecated and removed in future releases.
    """
    periodic_interest = 0

    def __init__(
        self, group, id, upb, coupon, floater_formula, floater_cap,
        floater_floor, prin_type, int_type, notional_with, delay, retail, macr,
        final_payment_date, cusip, schedule,
        dated_date=None, next_payment_date=None, child_tranches=[],
    ):
        self.group = group
        self.id = id
        self.original_upb = upb
        self.upb = upb
        self.coupon = coupon
        self.floater_formula = floater_formula
        self.floater_cap = floater_cap
        self.floater_floor = floater_floor
        self.prin_type = prin_type
        self.int_type = int_type
        self.notional_with = notional_with
        self.delay = delay
        self.retail = retail
        self.macr = macr
        self.dated_date = dated_date
        self.next_payment_date = next_payment_date
        self.final_payment_date = final_payment_date
        self.cusip = cusip
        self.schedule = schedule

        # These attributes are NOT referred to directly in the Terms Sheet.
        self.child_tranches = child_tranches

        self.cash_flows = {}
        self.periodic_cf = OrderedDict()
        self.periodic_prepay_scenario = "-1"
        self.pro_rated_ratio = dec('0')

        self.price_at_issuance = dec('1.00')
        self.assumed_price = dec('1.00')
        # This is a list of Notional tranches, whose interest was stripped from
        # this tranche. It is the corollary to the 'notional_with' attribute.
        # TODO: Need to actually populate this list during the loading of the
        # model!
        self.strips = []

    def new_child_tranche(
        self, group, id, upb, coupon, floater_formula, floater_cap,
        floater_floor, prin_type, int_type, notional_with, delay, retail, macr,
        final_payment_date, cusip, schedule,
        dated_date=None, next_payment_date=None, child_tranches=[],
    ):
        tranche = Tranche(
            group, id, upb, coupon, floater_formula, floater_cap,
            floater_floor, prin_type, int_type, notional_with, delay, retail,
            macr, final_payment_date, cusip, schedule,
            dated_date=None, next_payment_date=None, child_tranches=[],
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
        self.initialize_periodic_flow(period, payment_date)

    def initialize_periodic_flow(self, period, payment_date):
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
        self.name = name
        self.benchmark = benchmark
        self.fred_ticker = fred_ticker
        self.initial_rate = initial_rate
