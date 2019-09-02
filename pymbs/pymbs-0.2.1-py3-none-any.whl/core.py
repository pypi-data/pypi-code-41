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

from collections import namedtuple, OrderedDict
from datetime import datetime
from dateutil.relativedelta import *
import decimal
import json
import os
from typing import Generator, Optional, Union

import pandas as pd

from pymbs import payment_rules  # noqa
from pymbs.config import config
from pymbs.enums import ALL_GROUPS, ExitCode, PrepayBenchmark
from pymbs.exceptions import (
    AssumedCollatError, DateError,
    PrepaymentBenchmarkError, handle_gracefully
)
from pymbs.log import get_logger
from pymbs.utils import ACNT, _parse_waterfall, _round_dec

logger = get_logger(__name__)

dec = decimal.Decimal
d0 = dec('0')
d1 = dec('1')
d12 = dec('12')
d100 = dec('100')


def _load_assumed_collat() -> pd.DataFrame:
    if not config.terms_sheet:
        handle_gracefully(
            config._ipython_active,
            logger,
            'no_deal',
            exit_code=ExitCode.EX_CONFIG
        )
    else:
        ts = config.terms_sheet
    assumed_collat = pd.DataFrame.from_records(
        ts['assumed_collateral']['data'],
        columns=ts['assumed_collateral']['columns']
    )

    assumed_collat.index = range(1, len(assumed_collat) + 1)

    return assumed_collat


def _load_prepayment_scenarios(
        series_id: str,
        group_id: str) -> Union[Exception, dict, None]:

    pps_json = os.path.join(
        config.project_dir, f"{series_id}", f"{series_id}_pps.json"
    )
    try:
        with open(pps_json, 'r') as ppsj:
            pps = json.load(ppsj)
    except FileNotFoundError:
        print(f"No Terms Sheet exists for Series {series_id} at {pps_json}")
        return ExitCode.EX_NOINPUT

    for scenario_group in pps['prepayment_scenarios']:
        if scenario_group['group_id'] == group_id:
            return scenario_group
            break
    else:
        return None


def _run_collat_cf(group_id: str, repline_num: Optional[int] = 0) -> dict:
    # TODO: Run collateral cash flows for known collateral and securitzed
    # collateral too!
    assumed_collat = _load_assumed_collat()
    group_replines = assumed_collat[assumed_collat['group_id'] == group_id]

    if group_replines.empty:
        raise AssumedCollatError(group_id)

    # We're using itertuples() here to loop over the dataframe of the replines
    # belonging to one group. This looping isn't ideal, from a performance
    # perspective, but we anticipate that the given dataframe will always be
    # small enough that there shouldn't be much of an impact.
    if repline_num == 0:
        i = 0
        for repline in group_replines.itertuples():
            if i == 0:
                cash_flows = _run_repline_cf(repline)
                i += 1
            else:
                cf = _run_repline_cf(repline)
                cash_flows.add(cf, fill_value=0)
    else:
        row = group_replines[group_replines['repline'] == repline_num]
        try:
            repline = ACNT(*row.values[0])
        except IndexError:
            raise AssumedCollatError(group_id, repline_num)
        else:
            cash_flows = _run_repline_cf(repline)

    return cash_flows


def _run_repline_cf(repline: namedtuple) -> dict:
    ts = config.terms_sheet

    series_id = ts['meta']['series_id']
    group_id = repline.group_id
    pps = _load_prepayment_scenarios(series_id, group_id)

    prepayment_benchmark = pps.get('prepayment_benchmark')
    prepayment_speeds = pps.get('speeds')
    # TODO: Need to figure out how to handle prepayment vectors correctly
    prepayment_vector = pps.get('vector')

    if not (prepayment_benchmark and prepayment_speeds) or prepayment_vector:
        raise PrepaymentBenchmarkError(
            'None',
            ('You must provide either a Prepayment Benchmark and a Prepayment '
             'Speed, or a Prepayment Vector.')
        )

    payment_period = ts['meta'].get('payment_period')
    first_payment_date = datetime.strptime(
        ts['meta'].get('first_payment_date'),
        '%Y-%m-%d'
    )

    if not first_payment_date:
        raise DateError(
            'None',
            'You must provide a First Payment Date.'
        )

    if prepayment_benchmark and prepayment_speeds:
        cash_flows = {}
        benchmark = pps['prepayment_benchmark']
        for speed in pps['speeds']:
            sched = pd.DataFrame(
                _amortize_repline(
                    repline.upb,
                    repline.wac,
                    repline.wam,
                    repline.wala,
                    repline.coupon,
                    payment_period,
                    prepayment_benchmark,
                    speed,
                    prepayment_vector,
                    first_payment_date
                )
            )
            sched.index = range(1, len(sched) + 1)
            cash_flows[f"{speed} {benchmark}"] = sched

        return cash_flows


def _amortize_repline(
        orig_upb: decimal.Decimal,
        wac: decimal.Decimal,
        wam: int,
        wala: int,
        coupon: decimal.Decimal,
        payment_period: Optional[int] = 12,
        prepayment_benchmark: Optional[str] = None,
        prepayment_speed: Optional[float] = None,
        prepayment_vector: Optional[list] = [],
        start_date: Optional[datetime] = None) -> Generator:

    ctx = decimal.getcontext()
    ctx.prec = 18
    ctx.Emax = 12
    ctx.Emin = -10
    decimal.setcontext(ctx)
    payment_period = dec(payment_period)
    prepayment_speed = dec(prepayment_speed)
    # initialize the variables to keep track of
    # the periods and running balances
    p = d1
    beg_balance = orig_upb
    end_balance = orig_upb

    # The Simple Periodic Rate is the wac divided by the payment_period
    spr = (wac / d100) / payment_period

    # The Monthly Passthrough Rate is the coupon divided by the payment_period
    mpr = (coupon / d100) / payment_period

    while end_balance > 0:

        # Recalculate the interest based on the current balance
        # interest = round(((coupon / payment_period) * beg_balance), 2)
        interest = (mpr * beg_balance)

        # Determine Single Monthly Mortality Rate for Current Period
        numerator = spr * ((d1 + spr)**(wam - p + d1))
        denominator = ((d1 + spr)**(wam - p + d1)) - d1

        if denominator > dec('0.00001'):
            pmt = beg_balance * (numerator / denominator)
        else:
            pmt = beg_balance

        smm = _calculate_smm(
            prepayment_benchmark, prepayment_speed, wala, p
        )

        sched_principal = pmt - (spr * beg_balance)

        prepayment = (beg_balance - sched_principal) * smm

        # Ensure additional payment gets adjusted if the loan is being paid off
        prepay_principal = min(prepayment, beg_balance - sched_principal)
        total_principal = sched_principal + prepay_principal
        cash_flow = interest + total_principal
        end_balance = beg_balance - (sched_principal + prepay_principal)

        yield OrderedDict([
            ('period', p),
            ('payment_date', start_date),
            ('beginning_balance', beg_balance),
            ('smm', smm),
            ('scheduled_payment', pmt),
            ('net_interest', interest),
            ('scheduled_principal', sched_principal),
            ('prepayment', prepay_principal),
            ('total_principal', total_principal),
            ('cash_flow', cash_flow),
            ('ending_balance', end_balance)
        ])

        # Increment the counter, balance and date
        p += d1
        start_date += relativedelta(months=1)
        beg_balance = end_balance


def _calculate_smm(
        prepayment_benchmark: str,
        prepayment_speed: decimal.Decimal,
        wala: int,
        period) -> decimal.Decimal:

    if prepayment_benchmark == PrepayBenchmark.PSA.value:
        benchmark_cpr = dec('0.06')
        seasoned_period = dec('30')

        if (period + wala) < seasoned_period:
            cpr = benchmark_cpr * ((period + wala) / seasoned_period)
        else:
            cpr = benchmark_cpr
        smm = d1 - (d1 - ((prepayment_speed / d100) * cpr))**(d1 / d12)
    elif prepayment_benchmark == PrepayBenchmark.CPR.value:
        pass
    else:
        raise PrepaymentBenchmarkError(
            prepayment_benchmark,
            f"Unknown Prepayment Benchmark: {prepayment_benchmark}"
        )

    return smm


def _calculate_wal(
        cash_flow: pd.DataFrame,
        precision: int,
        collat_flag: Optional[bool] = False) -> decimal.Decimal:

    if collat_flag:
        principal = 'total_principal'
    else:
        principal = 'principal'
    cash_flow['period'] = cash_flow['period'].astype(str).transform(dec)
    wal = (sum(
        cash_flow['period'].apply(dec) * cash_flow[f"{principal}"]
    ) / (sum(cash_flow[f"{principal}"]) * d12))

    wal = _round_dec(wal, precision)

    return wal


def _prepare_wals(
        group_id: str,
        precision: decimal.Decimal,
        model: dict,
        _wals: dict) -> dict:

    _group = model['groups'][group_id]
    collat_cf = _group['collat_cf']
    for prepay_scenario, cash_flow in collat_cf.items():
        collat_flag = True
        tranche_id = f"Group {group_id} Collat"
        wal = _calculate_wal(cash_flow, precision, collat_flag)
        _wals['data'].append([group_id, tranche_id, prepay_scenario, wal])

    if model['groups'][group_id]['waterfall']:
        collat_flag = False
        for tranche_id in model['groups'][group_id]['tranches']:
            for prepay_scenario, cash_flow in \
                    _group['tranches'][tranche_id].cash_flows.items():
                    if tranche_id != "SB":
                        wal = _calculate_wal(cash_flow, precision, collat_flag)
                        _wals['data'].append(
                            [group_id, tranche_id, prepay_scenario, wal]
                        )
    return _wals


def _run_wals(
        group_id: str,
        precision: decimal.Decimal,
        model: dict) -> pd.DataFrame:

    _wals = {
        "columns": ["group_id", "tranche_id", "prepay_scenario", "wal"],
        "data": []
    }
    assumed_collat = _load_assumed_collat()
    if group_id == ALL_GROUPS:
        groups = assumed_collat['group_id'].unique()
        for group in groups:
            cash_flows = _run_collat_cf(group)
            if model['groups'][group]['waterfall']:
                model['groups'][group]['collat_cf'].update(cash_flows)
                tranches = _get_regular_tranches(model, group)
                _make_payments(model, group, cash_flows, tranches)
            else:
                cash_flows = _run_collat_cf(group)
                model['groups'][group]['collat_cf'].update(cash_flows)
            wals = _prepare_wals(group, precision, model, _wals)
    else:
        cash_flows = _run_collat_cf(group_id)
        if model['groups'][group_id]['waterfall']:
            model['groups'][group_id]['collat_cf'].update(cash_flows)
            tranches = _get_regular_tranches(model, group_id)
            _make_payments(model, group_id, cash_flows, tranches)
        else:
            model['groups'][group_id]['collat_cf'].update(cash_flows)
        wals = _prepare_wals(group_id, precision, model, _wals)

    wal_table = pd.DataFrame.from_records(
        wals['data'],
        columns=wals['columns']
    )

    return wal_table


def _get_regular_tranches(model: dict, group_id: str) -> list:

    tranches = []
    for tranche_id in model['groups'][group_id]['tranches']:
        tranche = model['groups'][group_id]['tranches'][tranche_id]
        if not tranche.macr:
            tranches.append(tranche)

    return tranches


def _make_payments(
        model: dict,
        group_id: str,
        cash_flows: pd.DataFrame,
        tranches: list) -> None:

    waterfall = model['groups'][group_id]['waterfall']
    if type(waterfall[0]) is str:
        waterfall = _parse_waterfall(model['groups'][group_id]['waterfall'])
    model['groups'][group_id]['waterfall'] = waterfall

    for prepay_scenario in cash_flows:
        collat_cf = cash_flows[prepay_scenario]
        for payment in collat_cf.itertuples():
            _pay_tranches(
                model, group_id, prepay_scenario, payment, tranches)

    for tranche in tranches:
        tranche.tabulate_cf()


def _pay_tranches(
        model: dict,
        group_id: str,
        prepay_scenario: str,
        payment: namedtuple,
        tranches: list) -> None:

    interest = payment.net_interest
    for tranche in tranches:
        tranche.new_periodic_cf(
            prepay_scenario,
            payment.period,
            payment.payment_date
        )
        interest = tranche.pay_interest(interest)
    _pay_waterfall(model, group_id, prepay_scenario, payment, tranches)
    for tranche in tranches:
        tranche.end_periodic_cf()


def _pay_waterfall(
        model: dict,
        group_id: str,
        prepay_scenario: str,
        payment: namedtuple,
        tranches: list) -> None:

    ctx = decimal.getcontext()
    ctx.prec = 18
    ctx.Emax = 12
    ctx.Emin = -10
    decimal.setcontext(ctx)
    waterfall = model['groups'][group_id]['waterfall']
    config.cache.update(
        model=model, prepay_scenario=prepay_scenario,
        group_id=group_id, payment=payment
    )
    for rule in waterfall:
        if rule['tranches']:
            tranches = [
                tranche for tranche in tranches if
                tranche.id in rule['tranches']
            ]
            config.cache.update(tranches=tranches)
        eval(f"payment_rules.{rule['func']}")
