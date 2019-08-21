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

from copy import copy
import decimal

from pymbs import config
from pymbs.utils import parse_expression, PNT

dec = decimal.Decimal

d0 = dec('0')
cleanup = dec('1E-2')


def calculate(bucket, exp):
    model = config.cache['model']  # noqa
    group_id = config.cache['group_id']  # noqa
    prepay_scenario = config.cache['prepay_scenario']  # noqa
    payment = config.cache['payment']  # noqa

    expression = parse_expression(exp)
    b = eval(expression)
    if 'buckets' in payment._fields:
        if payment.buckets[bucket]:
            payment.buckets[bucket] += b
        else:
            payment.buckets[bucket] = b
    else:
        this_bucket = f"{bucket[0]}"
        buckets = {this_bucket: b}
        payment = PNT(*list(payment), buckets)
        config.cache['payment'] = payment


def pay_accrual(bucket, tranche):
    pass


def pay_accrue(tranche_ids):
    tranches = config.cache['tranches']
    for tranche in tranches:
        tranche.pay_accrue()


def pay_pro_rata(bucket, tranches):
    ctx = decimal.getcontext()
    ctx.prec = 15
    ctx.Emax = 10
    ctx.Emin = -9
    decimal.setcontext(ctx)

    model = config.cache['model']  # noqa
    group_id = config.cache['group_id']  # noqa
    prepay_scenario = config.cache['prepay_scenario']  # noqa
    payment = config.cache['payment']
    current_payment = ctx.create_decimal(payment.buckets[bucket[0]])
    orig_current_payment = copy(current_payment)

    target_tranches = []
    for tranche_id in tranches:
        t = model['groups'][group_id]['tranches'][tranche_id]
        target_tranches.append(t)

    upb_sum = d0
    for tranche in target_tranches:
        upb_sum += tranche.upb

    if upb_sum > d0:
        for tranche in target_tranches:
            tranche.pro_rated_ratio = tranche.upb / upb_sum

    if (current_payment > d0 and upb_sum > d0):
        for tranche in target_tranches:
            projected_payment = \
                orig_current_payment * tranche.pro_rated_ratio
            actual_payment = min(
                projected_payment,
                tranche.upb,
                current_payment,
            )
            tranche.pay_principal(actual_payment)
            current_payment -= actual_payment
            if current_payment < cleanup:
                current_payment = d0
            payment.buckets[bucket[0]] = current_payment


def pay_sequential(bucket, tranches):
    ctx = decimal.getcontext()
    ctx.prec = 15
    ctx.Emax = 10
    ctx.Emin = -9
    decimal.setcontext(ctx)

    model = config.cache['model']  # noqa
    group_id = config.cache['group_id']  # noqa
    prepay_scenario = config.cache['prepay_scenario']  # noqa
    payment = config.cache['payment']
    current_payment = ctx.create_decimal(payment.buckets[bucket[0]])

    target_tranches = []
    for tranche_id in tranches:
        t = model['groups'][group_id]['tranches'][tranche_id]
        target_tranches.append(t)

    for tranche in target_tranches:
        if (current_payment > d0 and tranche.upb > d0):
            actual_payment = min(
                current_payment,
                tranche.upb,
            )
            tranche.pay_principal(actual_payment)
            current_payment -= actual_payment
            if current_payment < cleanup:
                current_payment = d0
            payment.buckets[bucket[0]] = current_payment


def pay_concurrent(bucket, tranches, ratios):
    pass
