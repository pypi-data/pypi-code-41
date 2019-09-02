import csv
import io
import itertools
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import goodtables
import importlib_resources
import requests
import tableschema
import tablib
from toolz import get_in, thread_first, update_in

import tabulator

from . import csv_helpers, loaders, messages
from .custom_checks import (cohesive_columns_value, compare_columns_value, extra_or_missing_header, french_siren_value,
                            french_siret_value, nomenclature_actes_value, sum_columns_value, year_interval_value)
from .spec import spec

log = logging.getLogger(__name__)

VALIDATA_MAX_ROWS = 100000


def replace_at(seq, index, item):
    """Replace seq[index] by item."""
    return (
        item if index == index1 else item1
        for index1, item1 in enumerate(seq)
    )


def prepend_error(report, table_index, error):
    return update_in(report, ["tables"], lambda tables: list(
        replace_at(tables, table_index, thread_first(
            tables[table_index],
            (update_in, ["errors"], lambda errors: [error] + errors),
            (update_in, ["error-count"], lambda error_count: error_count + 1),
        ))))


def improve_messages(report, schema):
    """Translate report error messages and add `title` and `content` fields"""
    if report is None:
        return None

    for table_id in range(report['table-count']):

        table = report['tables'][table_id]
        table['errors'] = messages.improve_messages(table['errors'], schema)

    return report


def compute_error_statistics(errors):
    """Computes error statistics as a dict:
    {
        'count': 12,
        'structure-errors': {
            'count': 1,
            'count-by-code': {
                'invalid-column-delimiter': 1
            }
        },
        'value-errors': {
            'count': 10,
            'rows-count': 3,
            'count-by-code': {
                'type-or-format-error': 2,
                'pattern-constraint': 7,
                'french-siret-value': 1,
            }
        },
    }
    """

    # Nb of errors by category
    errors_nb_dict = {'structure': 0, 'value': 0}

    # Errors distribution by category
    errors_dist_dict = {'structure': defaultdict(int), 'value': defaultdict(int)}

    # Fill in error stats
    for err in errors:
        err_tag = err['tag']
        errors_nb = len(err['message-data']['headers']) \
            if err['code'] in ('extra-headers', 'missing-headers') else 1
        errors_nb_dict[err_tag] += errors_nb
        errors_dist_dict[err_tag][err['code']] += errors_nb

    # Compute statistics
    return {
        'structure-errors': {
            'count': errors_nb_dict['structure'],
            'count-by-code': errors_dist_dict['structure'],
        },
        'value-errors': {
            'count': errors_nb_dict['value'],
            'rows-count': len(set([err['row-number'] for err in errors if err['tag'] == 'value'])),
            'count-by-code': errors_dist_dict['value'],
        },
        'count': errors_nb_dict['structure'] + errors_nb_dict['value']
    }


def amend_report(report):
    """tag 'structure' and 'value' error
    Remove 'value' errors if 'structure' errors
    Computes statistics
    """

    def categorize_err(err):
        """Computes error category: 'structure' or 'value'"""
        if err.get('column-number') is None and err.get('row-number') is None:
            return 'structure'
        return 'value'

    # Tag 'structure' or 'value'
    errors = [{**err, 'tag': categorize_err(err)} for err in report['tables'][0]['errors']]

    # Among value errors, only keep a single error by error cell
    # => the 1st encountered one
    filtered_errors = []
    row_col_set = set()
    for err in errors:
        if err['tag'] == 'value':
            row_col_id = '{}_{}'.format(err['row-number'], err.get('column-number', ''))
            if row_col_id in row_col_set:
                continue
            row_col_set.add(row_col_id)
        filtered_errors.append(err)
    errors = filtered_errors

    # Integrate enhanced errors into report
    report['tables'][0]['errors'] = errors
    report['tables'][0]['error-count'] = len(errors)

    # Store statistics
    stats = compute_error_statistics(errors)
    report['tables'][0]['error-stats'] = stats

    return report


def retrieve_schema_descriptor(schema):
    """Transforms a schema into a schema_descriptor

    `schema` can be either:
    - a `pathlib.Path`
    - a `str` containing either:
        - a file path
        - an URL
    - a `dict` representing the schema in JSON
    - a `tableschema.Schema` instance
    """
    if isinstance(schema, Path):
        schema = str(schema)
    if not isinstance(schema, tableschema.Schema):
        schema = tableschema.Schema(schema)
    return schema.descriptor


# Needed here because tablib Dataset doesn't allow empty column headers
EMPTY_HEADER = '__empty_header__'


def repair_core(dataset: tablib.Dataset, schema_field_names):
    """Core engine of repair function:
    Check tabular data and return transformed dataset and report log
    """
    report = []

    def append_col(dataset: tablib.Dataset, column_values, header):
        """work around a tablib bug on append_col,
        see https://github.com/vinayak-mehta/tablib/issues/33"""
        dataset.append_col(column_values, header=header)
        if dataset.headers is None:
            dataset.headers = [header]

    # Same field names, same order, just return dataset as is
    if dataset.headers == schema_field_names:
        return dataset, report

    # else, work!
    rows_nb = len(dataset.dict)
    content_dataset = tablib.Dataset()
    rejected_cols_dataset = tablib.Dataset()
    column_names_dict = dict()
    last_nonempty_header_col = None
    first_nonempty_header_col = None
    empty_header_cols = []
    duplicate_header_map = {}

    for i, head in enumerate(dataset.headers):

        # Don't keep empty header column
        if head == EMPTY_HEADER:
            empty_header_cols.append(i)
            continue

        # Remember first non-empty header
        if first_nonempty_header_col is None:
            first_nonempty_header_col = i

        # Remember last non-empty header
        last_nonempty_header_col = i

        # Move unknown columns in a special dataset
        if head not in schema_field_names:
            report.append(goodtables.Error(code='extra-header',
                                           message_substitutions={'column-name': head}))
            append_col(rejected_cols_dataset, dataset.get_col(i), head)
            continue

        # Rename and move duplicate columns in a special dataset
        if head in column_names_dict:
            ver = duplicate_header_map.get(head) or 1
            fixed_head = '{}~{}'.format(head, ver)
            duplicate_header_map[head] = ver + 1
            report.append(goodtables.Error(code='duplicate-header',
                                           message_substitutions={
                                               'column-name': head,
                                               'fixed-column-name': fixed_head,
                                               # not used by Validata but needed to avoid
                                               # a KeyError in message substitution
                                               'column_numbers': ''}))
            append_col(rejected_cols_dataset, dataset.get_col(i), fixed_head)

        # Normal case
        else:
            append_col(content_dataset, dataset.get_col(i), head)
            column_names_dict[head] = i

    # add blank-header errors
    def create_blank_header_error(col_id, pos_type, addon={}):
        return goodtables.Error(code='blank-header', message_substitutions={
            'column-number': col_id + 1,
            'position': pos_type,
            **addon
        })
    # With context to ease repairing
    for col_id in empty_header_cols:
        if col_id < first_nonempty_header_col:
            report.append(create_blank_header_error(col_id, 'leading'))
        elif col_id > last_nonempty_header_col:
            report.append(create_blank_header_error(col_id, 'trailing'))
        else:
            before_header = list(filter(lambda elt: elt != EMPTY_HEADER, dataset.headers[:col_id][::-1]))[0]
            after_header = list(filter(lambda elt: elt != EMPTY_HEADER, dataset.headers[col_id+1:]))[0]
            position_addon = {
                'before-header-name': before_header,
                'after-header-name': after_header,
            }
            report.append(create_blank_header_error(col_id, 'in', addon=position_addon))

    # Compare ordering
    if content_dataset.headers:
        schema_order_extract = [h for h in schema_field_names if h in content_dataset.headers]
        if content_dataset.headers != schema_order_extract:
            report.append(goodtables.Error(code='wrong-headers-order',
                                           message_substitutions={'actual-order': content_dataset.headers,
                                                                  'wanted-order': schema_order_extract}))

    # Then reorder and create empty columns if no content found
    fixed_dataset = tablib.Dataset()
    for h in schema_field_names:
        if content_dataset.headers and h in content_dataset.headers:
            col_id = content_dataset.headers.index(h)
            append_col(fixed_dataset, content_dataset.get_col(col_id), h)
        else:
            append_col(fixed_dataset, [''] * rows_nb, h)
            report.append(goodtables.Error(code='missing-header',
                                           message_substitutions={'column-number': i+1, 'column-name': h}))

    # Adds rejected columns at the end if any
    if len(rejected_cols_dataset) != 0:
        for i, h in enumerate(rejected_cols_dataset.headers):
            append_col(fixed_dataset, rejected_cols_dataset.get_col(i), h)

    return fixed_dataset, report


def repair(source, schema_descriptor, **repair_options):
    """Try to repair a `source` using a `schema
    Returns (fixed_source, report)
    """

    def to_inline_data(dataset):
        return [dataset.headers] + [dataset[i] for i in range(len(dataset))]

    def consume_source(source, **options):
        stream = tabulator.stream.Stream(source, **options)
        stream.open()

        # Get source headers
        headers = next(stream.iter())
        # And source body rows
        body_rows = list(stream.iter())

        return headers, body_rows

    # Gets schema content
    schema_field_names = [f.get('name') for f in schema_descriptor.get('fields')]

    # consume source to get headers and content
    try:
        headers, body_rows = consume_source(source, **repair_options)
    except StopIteration:
        return (source, [])

    # Create dataset for easier post processing
    dataset = tablib.Dataset(*body_rows, headers=[h if h else EMPTY_HEADER for h in headers])

    # Repair dataset!
    fixed_dataset, column_errors = repair_core(dataset, schema_field_names)

    # Return fixed source with potential errors
    return (to_inline_data(fixed_dataset), column_errors)


def validate(source, schema, with_repair=True, **options):
    """Validate a `source` using a `schema`."""

    schema_descriptor = retrieve_schema_descriptor(schema)

    base_options = {
        **options,
        "custom_loaders": loaders.custom_loaders,  # to use Validata BytesLoader
    }
    fixed_source, structure_errors = source, None
    checks = ['structure', 'schema', {'extra-or-missing-header': {}}]
    if with_repair:
        fixed_source, structure_errors = repair(source, schema_descriptor, **base_options)
        checks = ['structure', 'schema']

    custom_checks_config = schema_descriptor.get('custom_checks')
    if custom_checks_config:
        for custom_check_conf in custom_checks_config:
            checks.append({custom_check_conf['name']: custom_check_conf['params']})
    inspector = goodtables.Inspector(
        checks=checks,
        skip_checks=['non-matching-header', 'extra-header', 'missing-header'],
        row_limit=VALIDATA_MAX_ROWS,
    )

    options = {**base_options}
    if with_repair:
        options['scheme'] = 'stream'
        options['format'] = 'inline'
    report = inspector.inspect(source=fixed_source, schema=schema_descriptor, **options)

    if report['tables'][0].get('format') == "csv" and not any(
        get_in(['errors', err['code'], 'type'], spec, default=None) == 'source'
        for err in report['tables'][0]['errors']
    ):
        standard_csv_delimiter = ","
        dialect = csv_helpers.detect_dialect(fixed_source, **options)
        if dialect is None:
            error = goodtables.Error(code='unknown-csv-dialect')
            report = prepend_error(report, table_index=0, error=dict(error))
        else:
            detected_delimiter = dialect.delimiter
            if detected_delimiter != standard_csv_delimiter:
                error = goodtables.Error(
                    code='invalid-column-delimiter',
                    message_substitutions={
                        "detected": detected_delimiter,
                        "expected": standard_csv_delimiter,
                    },
                )
                report = prepend_error(report, table_index=0, error=dict(error))

    # If some errors have been encountered during repair process
    if structure_errors:
        for structure_err in structure_errors[::-1]:
            report = prepend_error(report, table_index=0, error=dict(structure_err))

    # Translate error messages
    report = improve_messages(report, schema_descriptor)

    # Tag errors ('structure' or 'value')
    # Compute statistics
    report = amend_report(report)

    # Add date
    report['date'] = datetime.now(timezone.utc).isoformat()

    return report


def compute_badge(report, config) -> dict:
    """Compute badge from report statistics and badge configuration."""

    def build_badge(structure_status, body_status=None, error_ratio=None):
        """Badge info creation"""
        if structure_status == 'KO':
            return {
                "structure": 'KO'
            }
        return {
            "structure": structure_status,
            "body": body_status,
            "error-ratio": error_ratio
        }

    # Gets stats from report
    stats = report['tables'][0]['error-stats']

    # And total number of cells
    column_count = len(report['tables'][0]['headers'])
    row_count = report['tables'][0]['row-count']
    cell_total_number = column_count * row_count

    # No errors
    if stats['count'] == 0:
        return build_badge('OK', 'OK', 0.0)

    # Structure part
    structure_status = None
    if stats['structure-errors']['count'] == 0:
        structure_status = 'OK'
    else:
        cbc = stats['structure-errors']['count-by-code']
        if len(cbc) == 1 and 'invalid-column-delimiter' in cbc:
            structure_status = 'WARN'
        else:
            # structure_status = 'KO'
            return build_badge('KO')

    # body part
    value_errors = stats['value-errors']
    if value_errors['count'] == 0:
        return build_badge(structure_status, 'OK', 0.0)

    # Computes error ratio
    weight_dict = config['body']['errors-weight']
    ratio = sum([nb * weight_dict.get(err, 1.0) for err, nb in value_errors['count-by-code'].items()]) \
        / cell_total_number
    body_status = 'WARN' if ratio < config['body']['acceptability-threshold'] else 'KO'

    return build_badge(structure_status, body_status, ratio)
