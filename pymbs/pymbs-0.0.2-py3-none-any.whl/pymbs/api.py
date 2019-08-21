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

import decimal
import json
import os
from typing import Optional, TextIO

import pandas as pd

from pymbs import config, core
from pymbs.enums import ExitCode
from pymbs.tranche import IndexRate, Tranche

__all__ = ['load_deal', 'load_assumed_collat', 'load_model', 'run_collat_cf',
           'show_wals', 'load_tranches', 'disperse_cf']


pd.set_option('display.max_rows', config.max_rows)
pd.set_option('precision', config.default_precision)


def load_deal(series_no: int) -> dict:
    """Load the Terms Sheet for the REMIC Series number provided.

    The Terms Sheet is essential for modeling the deal. If this function is
    not called at the start, most of the other functions will fail.

    Within the PROJECT_DIR, specified in the user's configuration file, it is
    expected that there will be one subdirectory for each REMIC Series number.
    Inside the Series directory, it is expected that the Terms Sheet will be
    a file named `series`_ts.json, where `series` refers to the actual Series
    number.

    Args:
        series_no: The REMIC Series number.

    Returns:
        A dictionary object, representing the Terms Sheet.
        If the Terms Sheet file is not located, returns Exit Code 66.

    Example:
        Given: REMIC Series Number is 2618

        Path: /PROJECT_DIR/2618/2618_ts.json
    """
    ts_json = os.path.join(
        config.PROJECT_DIR, f"{series_no}", f"{series_no}_ts.json"
    )
    try:
        with open(ts_json, 'r') as tsj:
            config.terms_sheet = json.load(tsj, parse_float=decimal.Decimal)
    except FileNotFoundError:
        print(f"No Terms Sheet exists for Series {series_no} at {ts_json}")
        return ExitCode.EX_NOINPUT

    return config.terms_sheet


def load_assumed_collat() -> pd.DataFrame:
    """Load the Assumed Collateral replines from the Terms Sheet.

    This assumes that the Terms Sheet has already been loaded, using the
    load_deal function.

    This will *only* load Assumed Collateral. PyMBS does not yet have the
    ability to handle Known Collateral or Securitzed Collateral. It can
    however handle multiple Assumed replines per group.
    """
    assumed_collat = core.load_assumed_collat()

    return assumed_collat


def load_model(model_json: TextIO) -> dict:
    """Load the structured cash flow model from the Terms Sheet, supplemented
    by the model file.

    The Terms sheet does NOT include the pay rule waterfall or specific
    benchmark interest rate information used by the model. These are provided
    in a separate JSON file.

    Within the PROJECT_DIR, specified in the user's configuration file, it is
    expected that there will be one subdirectory for each REMIC Series number.
    Inside the Series directory, it is expected that the Model File named as
    provided as argument to this function will exist.

    Args:
        model_json: The name of the model file inside the Series directory.

    Returns:
        A dictionary object, representing the structured cash flow model.
        If the Model file is not located, returns Exit Code 66.

    Example:
        Given: model_json = '2618_model.json'

        Path: /PROJECT_DIR/2618/2618_model.json
    """
    if not config.terms_sheet:
        print(f"{config.no_deal}")
        return ExitCode.EX_CONFIG
    else:
        ts = config.terms_sheet
    series_no = ts['meta']['series_no']
    model_file = os.path.join(
        config.PROJECT_DIR, f"{series_no}", f"{series_no}_model.json"
    )
    try:
        with open(model_file, 'r') as tsj:
            mf = json.load(tsj, parse_float=decimal.Decimal)
    except FileNotFoundError:
        print(f"No model exists for Series {series_no} at {model_file}")
        return ExitCode.EX_NOINPUT
    groups = {}
    indices = {}
    for tranche in ts['tranches']['data']:
        tranche_group = tranche[0]
        if tranche_group not in groups:
            groups[tranche_group] = {}
    for group in groups:
        groups[group]['tranches'] = {}
        if group is not 0:
            groups[group]['collat_cf'] = {}
            groups[group]['waterfall'] = []
    first_payment_dates = ts['tranches']['first_payment_dates']
    for tranche in ts['tranches']['data']:
        tranche_group = tranche[0]
        tranche_id = tranche[1]
        groups[tranche_group]['tranches'][tranche_id] = Tranche(
            *tranche,
            dated_date=ts['meta']['issue_date'],
            next_payment_date=first_payment_dates[str(tranche_group)]
        )
    for group in groups:
        if group is not 0:
            groups[group]['waterfall'].extend(mf['waterfall'][str(group)])
    for index in mf['indices']:
        indices[index['name']] = IndexRate(**index)
    config.model = {}
    config.model['groups'] = groups
    config.model['indices'] = indices

    return config.model


def run_collat_cf(
    group_id: Optional[int] = -1,
    repline_num: Optional[int] = -1
) -> dict:
    """Run cash flows from Assumed Collateral replines specified in the
    Terms Sheet. A Pandas DataFrame is created for each cash flow prepayment
    scenario, as specified in the Prepayment Scenarios JSON file.

    The Terms sheet does NOT include the pay rule waterfall or specific
    benchmark interest rate information used by the model. These are provided
    in a separate JSON file.

    Within the PROJECT_DIR, specified in the user's configuration file, it is
    expected that there will be one subdirectory for each REMIC Series number.
    Inside the Series directory, it is expected that the Model File named as
    provided as argument to this function will exist.

    Args:
        group_id: The number of the Group for which to run the cash flows.
                  By default, this value is set to -1, which will run
                  cash flows for ALL groups in the deal at the Prepayment
                  Scenarios specified for each group.

        repline_num: Optionally, the user may specify running the cash flows
                     for a specific repline in a specific group, if the group
                     has more than one assumed repline.

    Returns:
        A dictionary object, containing a Pandas Dataframe for the cash flow
        calculated at each Prepayment Scenario.

    Example:
        Path: /PROJECT_DIR/2618/2618_pps.json
    """
    # TODO: Run collateral cash flows for known collateral and securitzed
    # collateral too!
    cash_flows = core.run_collat_cf(group_id, repline_num=0)

    return cash_flows


def show_wals(
    group_id: Optional[int] = -1,
    precision: Optional[int] = config.default_precision
) -> pd.DataFrame:
    """Calulate the Weigted Average Lives (WALs) of all Regular tranches in the
    group specified, including those for the collateral. Currently WALs are NOT
    calcuated for Notional or MACR classes. This functionality will be exposed
    in a future release.

    If no Group number is specified in the call to this function, WALs will
    be calculated for all groups in the deal. This is not necessarily
    desireable, as the Prepayment Scenarios will be different for different
    groups, so the table that is returned will contain a number of 'missing'
    values. An enhancement to handle this gracefully will be provided in a
    future release. In the meantime, it is recommended that the user specify
    a group number when calling this function.

    Args:
        group_id: The number of the Group for which to run the WALs.
                  By default, this value is set to -1, which will run
                  WALs for ALL groups in the deal at the Prepayment
                  Scenarios specified for each group.

        precision: The precision of the calculated WALs may be optionally
                   specified. If not specifed, it will use the
                   default_precision specified in the configuration
                   file. At this time, this value is set to 10 decimal places,
                   which is almost always sufficient for tying-out the cash
                   flows with a counter-party. The precision of the WALs
                   disclosed in the Prospectus Supplement is 1 decimal.

    Returns:
        A Pandas Dataframe showing the WALs for each tranche, calulated based
        on the cash flows run at each Prepayment Sceanrio specified for the
        group.
    """
    if not config.model:
        print(f"{config.no_deal}")
        return ExitCode.EX_CONFIG
    else:
        model = config.model
    wals = core.run_wals(group_id, precision, model)
    column_order = [wal for wal in wals['prepay_scenario'].unique()]

    def f(x):
        return (x.pivot('tranche_id', 'prepay_scenario', 'wal'))

    _wal_table = wals.groupby('group_id', group_keys=True).apply(f)
    wal_table = _wal_table.reindex(columns=column_order)

    return wal_table


def load_tranches(group_id: Optional[int] = -1) -> pd.DataFrame:
    """Load the tranches for the deal, or for the group specified, into a
    Pandas Dataframe for easy display in the Jupyter Notebook.

    Args:
        group_id: The number of the Group for which to load the tranches.
                  By default, this value is set to -1, which will load
                  the tranches for ALL of groups in the deal. As per
                  convention, the Residual tranches will appear in
                  Group 0.

    Returns:
        A Pandas Dataframe showing Tranche details for each tranche queried.
    """
    if not config.terms_sheet:
        print(f"{config.no_deal}")
        return ExitCode.EX_CONFIG
    else:
        ts = config.terms_sheet

    tranches = pd.DataFrame.from_records(
        ts['tranches']['data'],
        columns=ts['tranches']['columns']
    )

    if group_id < 0:
        tranches = tranches
    else:
        tranches = tranches[tranches['group_id'] == group_id]

    tranches.index = range(1, len(tranches) + 1)

    return tranches


def disperse_cf(model: dict, group_id: Optional[int] = -1) -> int:
    """Make all payments of Interest and Principal, based on the rules
    enumerated in the model.

    Args:
        group_id: The number of the Group for which to load the tranches.
                  By default, this value is set to -1, which will load
                  the tranches for ALL of groups in the deal. As per
                  convention, the Residual tranches will appear in
                  Group 0.

    Returns:
        ExitCode 0 on success. After this function has returned, the cash flows
        for each tranche, including the collateral, will be accessible from
        within the model.
    """
    if group_id < 0:
        for group in model['groups']:
            cash_flows = run_collat_cf(group)
            model['groups'][group]['collat_cf'].update(cash_flows)
            tranches = core.get_regular_tranches(model, group)
            core.make_payments(model, group, cash_flows, tranches)
    else:
        cash_flows = run_collat_cf(group_id)
        model['groups'][group_id]['collat_cf'].update(cash_flows)
        tranches = core.get_regular_tranches(model, group_id)
        core.make_payments(model, group_id, cash_flows, tranches)

    return ExitCode.EX_SUCCESS
