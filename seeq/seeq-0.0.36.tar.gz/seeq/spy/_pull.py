import queue
import threading

import pandas as pd
import numpy as np

from seeq.sdk import *

from . import _common
from . import _login


def pull(items, start=None, end=None, grid='15min', header='__auto__', capsules_as='auto', tz_convert=None,
         calculation=None, errors='raise', quiet=False):
    _common.validate_timezone_arg(tz_convert)
    _common.validate_errors_arg(errors)

    if not (isinstance(items, (pd.DataFrame, pd.Series))):
        raise RuntimeError('items argument must be a pandas.DataFrame or pandas.Series')

    if not items.index.is_unique:
        raise RuntimeError("The items DataFrame's index must be unique. Use reset_index(drop=True, inplace=True) "
                           "before passing in to spy.pull().")

    if isinstance(calculation, pd.DataFrame):
        if len(calculation) != 1:
            raise RuntimeError("When applying a calculation across assets, calculation argument must be a one-row "
                               "DataFrame, or a Series. When applying a calculation to a signal/condition/scalar, "
                               'calculation must be a string with a signal variable in it: $signal, $condition or '
                               '$scalar.')

        calculation = calculation.iloc[0]

    if isinstance(items, pd.Series):
        items = pd.DataFrame().append(items)

    if capsules_as not in ['auto', 'capsules', 'signals']:
        raise RuntimeError("capsules_as must be one of 'auto', 'capsules', 'signals'")

    if end is None:
        end = pd.datetime.now()
        if start is not None and start > end:
            end = start + pd.Timedelta(hours=1)

    if start is None:
        start = pd.datetime.now() if end is None else end
        start = start - pd.Timedelta(hours=1)

    pd_start = pd.to_datetime(start)  # type: pd.Timestamp
    pd_end = pd.to_datetime(end)  # type: pd.Timestamp

    status_columns = list()
    if 'ID' in items:
        status_columns.append('ID')
    if 'Path' in items:
        status_columns.append('Path')
    if 'Asset' in items:
        status_columns.append('Asset')
    if 'Name' in items:
        status_columns.append('Name')

    status_df = items[status_columns].copy()
    status_df['Count'] = 0
    status_df['Time'] = 0
    status_df['Result'] = 'Pulling'

    _common.display_status('Pulling data from %s to %s' % (pd_start, pd_end), _common.STATUS_RUNNING, quiet,
                           status_df)

    items_api = ItemsApi(_login.client)
    formulas_api = FormulasApi(_login.client)

    query_df = items  # type: pd.DataFrame
    output_df = pd.DataFrame()
    at_least_one_signal = False
    column_names = dict()
    final_column_names = list()
    for phase in ['signals', 'conditions', 'scalars', 'final']:
        threads = list()
        try:
            pulled_series = queue.Queue()
            status_updates = queue.Queue()

            def _drain_status_updates():
                while True:
                    try:
                        _index, _message, _count, _time = status_updates.get_nowait()
                        status_df.at[_index, 'Result'] = _message
                        status_df.at[_index, 'Count'] = _count
                        status_df.at[_index, 'Time'] = _time
                    except queue.Empty:
                        break

                _common.display_status(
                    'Pulling from <strong>%s</strong> to <strong>%s</strong>' % (pd_start, pd_end),
                    _common.STATUS_RUNNING, quiet, status_df)

            for index, row in query_df.iterrows():
                try:
                    output_df, at_least_one_signal = _process_query_row(
                        _drain_status_updates, at_least_one_signal, calculation, capsules_as,
                        column_names, final_column_names, formulas_api, grid, header, index,
                        items_api, output_df, pd_end, pd_start, phase, pulled_series, row,
                        status_df, status_updates, threads, tz_convert)

                except BaseException as e:
                    if errors == 'raise':
                        raise

                    status_df.at[index, 'Result'] = _common.format_exception(e)

            still_running = True
            while still_running:
                _drain_status_updates()

                still_running = False
                for _, thread in threads:
                    thread.join(0.1)

                    if thread.is_alive():
                        still_running = True
                        break

            _drain_status_updates()

            for item_name, series in list(pulled_series.queue):
                output_df = output_df.join(pd.DataFrame({item_name: series}), how='outer')

        except KeyboardInterrupt:
            for stop_event, _ in threads:
                stop_event.set()

            status_df['Result'] = 'Canceled'
            _common.display_status('Pull canceled', _common.STATUS_CANCELED, quiet, status_df)
            return None

    _common.display_status('Pull successful from <strong>%s</strong> to <strong>%s</strong>' % (pd_start, pd_end),
                           _common.STATUS_SUCCESS, quiet, status_df)

    # We add these columns to the items DataFrame that was passed in so that the caller can inspect the Result field
    # programmatically. In Jupyter, you can see the Result field in the display, so these extra columns are mostly
    # useful in non-Jupyter scenarios. This approach avoids having to return a tuple at all times.
    items['Pull Count'] = status_df['Count']
    items['Pull Time'] = status_df['Time']
    items['Pull Result'] = status_df['Result']

    # Ensures that the order of the columns matches the order in the metadata
    return output_df[final_column_names]


def _process_query_row(_drain_status_updates, at_least_one_signal, calculation, capsules_as, column_names,
                       final_column_names, formulas_api, grid, header, index, items_api, output_df, pd_end, pd_start,
                       phase, pulled_series, row, status_df, status_updates, threads, tz_convert):
    if phase == 'signals' and not _common.present(row, 'ID'):
        status_df.at[index, 'Result'] = 'No "ID" column - skipping'
        return output_df, at_least_one_signal

    item_id, item_name, item_type = _get_item_details(header, items_api, row)
    calculation_to_use = calculation
    if item_type == 'Asset':
        if calculation is None:
            raise RuntimeError('To pull data for an asset, you must provide a "calculate" argument whose '
                               'value is the metadata of a calculation that is based on a single asset.')

        swap_input = SwapInputV1()
        swap_input.swap_in = item_id
        calc_item_id, _, item_type = _get_item_details(header, items_api, calculation)

        item_dependency_output = items_api.get_formula_dependencies(
            id=calc_item_id)  # type: ItemDependencyOutputV1

        unique_assets = set(dep.ancestors[-1].id
                            for dep in item_dependency_output.dependencies
                            if len(dep.ancestors) > 0)

        if len(unique_assets) != 1:
            raise RuntimeError('To pull data for an asset, the "calculate" parameter must be a calculated '
                               'item that involves only one asset.')

        swap_input.swap_out = unique_assets.pop()

        swapped_item = items_api.find_swap(id=calc_item_id, body=[swap_input])  # type: ItemPreviewV1

        item_id = swapped_item.id

        # Don't try to apply a calculation later, we've already done it via our swap activity
        calculation_to_use = None

    if phase == 'signals' and \
            'Signal' not in item_type and 'Condition' not in item_type and 'Scalar' not in item_type:
        status_df.at[index, 'Result'] = 'Not a Signal, Condition or Scalar - skipping'
        return output_df, at_least_one_signal

    if 'Signal' in item_type:
        at_least_one_signal = True

    if phase == 'signals' and 'Signal' in item_type:

        parameters = ['signal=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$signal'

        if grid:
            formula = 'resample(%s, %s)' % (formula, grid)

        stop_event = threading.Event()
        thread = threading.Thread(target=_pull_signal, args=(formulas_api, formula, parameters, item_id,
                                                             item_name, pulled_series, pd_start, pd_end,
                                                             tz_convert, column_names, stop_event,
                                                             status_updates, index))

        thread.start()
        threads.append((stop_event, thread))

    elif phase == 'conditions' and 'Condition' in item_type:
        if capsules_as == 'capsules' and at_least_one_signal:
            raise RuntimeError('Pull cannot include signals when conditions present and "capsules_as" '
                               'parameter is "capsules"')

        if capsules_as == 'auto':
            capsules_as = 'signals' if at_least_one_signal else 'capsules'

        if capsules_as == 'signals' and not at_least_one_signal:
            if grid is None:
                raise RuntimeError(
                    'Pull cannot include conditions when no signals present with capsules_as='
                    'capsules and grid=None')

            placeholder_item_name = '__placeholder__'
            _pull_signal(formulas_api, '0.toSignal(%s)' % grid, list(), placeholder_item_name,
                         placeholder_item_name, pulled_series, pd_start, pd_end, tz_convert, dict(),
                         threading.Event())

            _, series = pulled_series.get(True, 30)
            output_df[placeholder_item_name] = series

        parameters = ['condition=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$condition'

        output_df = _pull_condition(capsules_as, formulas_api, formula, parameters, item_id,
                                    item_name, output_df, pd_start, pd_end, tz_convert,
                                    column_names, index, status_df, _drain_status_updates)

    elif phase == 'scalars' and 'Scalar' in item_type:
        parameters = ['scalar=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$scalar'

        _pull_scalar(formulas_api, formula, parameters, item_id, item_name, output_df, column_names, index,
                     status_df, _drain_status_updates)

    elif phase == 'final':
        if item_id in column_names:
            for column_name in column_names[item_id]:
                if column_name not in final_column_names:
                    final_column_names.append(column_name)

    return output_df, at_least_one_signal


def _convert_column_timezone(ts_column, tz):
    ts_column = ts_column.tz_localize('UTC')
    return ts_column.tz_convert(tz) if tz else ts_column


def _pull_condition(capsules_as, formulas_api, formula, parameters, item_id, item_name, output_df, pd_start, pd_end,
                    tz, column_names, status_index, status_df, _drain_status_updates):
    try:
        timer = _common.timer_start()
        capsule_count = 0
        current_start = pd_start.value
        offset = 0
        while True:
            formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
                formula=formula,
                parameters=parameters,
                start='%d ns' % current_start,
                end='%d ns' % pd_end.value,
                offset=offset,
                limit=_common.DEFAULT_PULL_PAGE_SIZE)  # type: FormulaRunOutputV1

            next_start = current_start
            capsules_output = formula_run_output.capsules  # type: CapsulesOutputV1
            check_for_dupes = True

            columns = dict()
            if capsules_as == 'signals':
                columns[item_name] = pd.Series()
                starting_capsule_index = 0
                for _index, _ in output_df.iterrows():
                    for i in range(starting_capsule_index, len(capsules_output.capsules)):
                        capsule = capsules_output.capsules[i]  # type: CapsuleV1
                        capsule_start = _index if pd.isna(capsule.start) else _common.convert_to_timestamp(
                            capsule.start, tz)
                        capsule_end = _index if pd.isna(capsule.end) else _common.convert_to_timestamp(capsule.end, tz)
                        if not pd.isna(capsule.start) and _common.convert_to_timestamp(capsule.start, tz) > next_start:
                            next_start = _common.convert_to_timestamp(capsule.start, tz)
                        present = capsule_start <= _index <= capsule_end
                        if capsule_end < _index:
                            starting_capsule_index = i
                        columns[item_name].at[_index] = 1 if present else 0
                        for prop in capsule.properties:  # type: ScalarPropertyV1
                            colname = '%s - %s' % (item_name, prop.name)
                            if colname not in columns:
                                columns[colname] = pd.Series()
                            columns[colname].at[_index] = prop.value if present else np.nan

                column_names[item_id] = list()
                for col, series in columns.items():
                    output_df[col] = series
                    column_names[item_id].append(col)
            else:
                capsule_df_rows = list()

                for capsule in capsules_output.capsules:
                    column_names[item_id] = ['Condition', 'Capsule Start', 'Capsule End']
                    if check_for_dupes and \
                            'Condition' in output_df and \
                            'Capsule Start' in output_df and \
                            'Capsule End' in output_df and \
                            len(output_df.loc[(output_df['Condition'] == item_name) &
                                              (output_df['Capsule Start'] == _common.convert_to_timestamp(capsule.start,
                                                                                                          tz)) &
                                              (output_df['Capsule End'] == _common.convert_to_timestamp(capsule.end,
                                                                                                        tz))]):
                        # This can happen as a result of pagination
                        continue

                    check_for_dupes = False

                    capsule_dict = {
                        'Condition': item_name,
                        'Capsule Start': _common.convert_to_timestamp(capsule.start, tz),
                        'Capsule End': _common.convert_to_timestamp(capsule.end, tz)
                    }

                    for prop in capsule.properties:  # type: ScalarPropertyV1
                        capsule_dict[prop.name] = prop.value
                        column_names[item_id].append(prop.name)

                    capsule_df_rows.append(capsule_dict)

                    if not pd.isna(capsule.start) and capsule.start > next_start:
                        next_start = capsule.start

                output_df = output_df.append(capsule_df_rows)

            # Note that capsule_count here can diverge from the exact count in the output due to pagination
            capsule_count += len(capsules_output.capsules)

            if len(capsules_output.capsules) < _common.DEFAULT_PULL_PAGE_SIZE:
                break

            if next_start == current_start:
                # This can happen if the page is full of capsule that all have the same start time
                offset += _common.DEFAULT_PULL_PAGE_SIZE
            else:
                offset = 0

            current_start = next_start

            status_df.at[status_index, 'Result'] = 'Pulling %s' % _common.convert_to_timestamp(current_start, tz)
            status_df.at[status_index, 'Count'] = capsule_count
            status_df.at[status_index, 'Time'] = _common.timer_elapsed(timer)

            _drain_status_updates()

        status_df.at[status_index, 'Result'] = 'Success'
        status_df.at[status_index, 'Count'] = capsule_count
        status_df.at[status_index, 'Time'] = _common.timer_elapsed(timer)

    except BaseException as e:
        import traceback
        status_df.at[status_index, 'Result'] = str(traceback.format_exc())

    return output_df


def _pull_signal(formulas_api, formula, parameters, item_id, item_name, pulled_series, pd_start, pd_end, tz,
                 column_names, stop_event=None, status_updates=None, index=None):
    try:
        series = pd.Series()
        timer = _common.timer_start()
        current_start = pd_start
        last_key = 0
        while not stop_event.is_set():
            formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
                formula=formula,
                parameters=parameters,
                start='%d ns' % current_start.value,
                end='%d ns' % pd_end.value,
                offset=0,
                limit=_common.DEFAULT_PULL_PAGE_SIZE)  # type: FormulaRunOutputV1

            timings = _common.get_timings(http_headers)

            series_samples_output = formula_run_output.samples  # type: SeriesSamplesOutputV1

            time_index = _convert_column_timezone(pd.DatetimeIndex([sample_output.key for sample_output in
                                                                    series_samples_output.samples if
                                                                    sample_output.key > last_key]), tz)

            series = series.append(pd.Series([sample_output.value for sample_output in
                                              series_samples_output.samples if sample_output.key > last_key],
                                             index=time_index))

            if len(series_samples_output.samples) < _common.DEFAULT_PULL_PAGE_SIZE:
                break

            if len(series) > 0:
                last_key = series.index[-1].value

            if time_index[-1].value > current_start.value:
                current_start = time_index[-1]

            if status_updates is not None:
                status_updates.put((index, 'Pulling: %s' % str(current_start),
                                    len(series), _common.timer_elapsed(timer)))

        column_names[item_id] = [item_name]
        if status_updates is not None:
            status_updates.put((index, 'Success', len(series), _common.timer_elapsed(timer)))
        pulled_series.put((item_name, series))

    except BaseException as e:
        if status_updates is not None:
            status_updates.put((index, str(e), None, None))


def _pull_scalar(formulas_api, formula, parameters, item_id, item_name, output_df, column_names, status_index,
                 status_df, _drain_status_updates):
    timer = _common.timer_start()

    formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
        formula=formula,
        parameters=parameters)  # type: FormulaRunOutputV1

    if len(output_df.index) == 0:
        output_df.at[0, item_name] = formula_run_output.scalar.value
    else:
        output_df[item_name] = formula_run_output.scalar.value

    column_names[item_id] = [item_name]

    status_df.at[status_index, 'Result'] = 'Success'
    status_df.at[status_index, 'Count'] = 1
    status_df.at[status_index, 'Time'] = _common.timer_elapsed(timer)


def _get_item_details(header, items_api, row):
    item_id = _common.get(row, 'ID')
    item = None
    if _common.present(row, 'Type'):
        item_type = _common.get(row, 'Type')
    else:
        item = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1
        item_type = item.type
    if header.upper() == 'ID':
        item_name = item_id
    elif _common.present(row, header):
        item_name = _common.get(row, header)
    else:
        if not item:
            item = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1

        item_name = ''
        if header == '__auto__' and _common.present(row, 'Path'):
            item_name = _common.get(row, 'Path') + ' >> '
            if _common.present(row, 'Asset'):
                item_name += _common.get(row, 'Asset') + ' >> '

        if header in ['__auto__', 'Name']:
            item_name += item.name
        elif header == 'Description':
            item_name += item.description
        else:
            prop = [p.value for p in item.properties if p.name == header]
            if len(prop) == 0:
                item_name += item_id
            else:
                item_name += prop[0]

    return item_id, item_name, item_type
