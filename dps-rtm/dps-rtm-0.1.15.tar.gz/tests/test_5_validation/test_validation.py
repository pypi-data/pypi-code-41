"""
Unit tests for validation.py functions
"""

# --- Standard Library Imports ------------------------------------------------
from collections import namedtuple

# --- Third Party Imports -----------------------------------------------------
import pytest

# --- Intra-Package Imports ---------------------------------------------------
import rtm.validate.validation as val
import rtm.main.context_managers as context
from rtm.containers.fields import Fields
from rtm.containers.work_items import WorkItems


def test_column_exist(capsys):
    io = [
        (True, f"\tPass\tFIELD EXIST\n"),
        (False, f"\tError\tFIELD EXIST - Field not found\n"),
    ]
    for item in io:
        result = val.val_column_exist(item[0])
        result.print()
        captured = capsys.readouterr()
        assert captured.out == item[1]


@pytest.mark.parametrize("reverse", [False, True])
def test_column_sort(fix_fields, reverse):

    fields = fix_fields("Procedure Based Requirements")
    scores_should = ["Pass"] * len(fields)

    if reverse:
        fields = list(reversed(fields))
        scores_should = ["Pass"] + ["Error"] * (len(fields) - 1)

    with context.fields.set(fields):
        scores_actual = [val.val_column_sort(field).score for field in fields]

    assert len(scores_actual) > 0
    assert scores_actual == scores_should


def test_cells_not_empty():
    passing_values = [True, False, "hello", 42]
    failing_values = [None, ""]
    values = failing_values + passing_values

    failing_indices = list(range(len(failing_values)))
    results = val.val_cells_not_empty(values)
    assert results.indices == failing_indices


@pytest.mark.skip("This is not a standalone test func. It gets passed as a parameter further down.")
def test_cascade_level_not_empty():
    fields = context.fields.get()
    cascade_field = fields.get_matching_field('CascadeLevel')
    results = val.val_cells_not_empty(cascade_field.body)
    return results


@pytest.mark.skip("This is not a standalone test func. It gets passed as a parameter further down.")
def test_valid_cascade_levels():
    fields = context.fields.get()
    cascade_field = fields.get_matching_field('CascadeLevel')
    results = val.valid_cascade_levels(cascade_field)
    return results


CascadeValidation = namedtuple("CascadeValidation", "func header")
cascade_validations = [
    CascadeValidation(func=val.val_cascade_block_not_empty, header="not_empty"),
    CascadeValidation(func=val.val_cascade_block_only_one_entry, header="one_entry"),
    CascadeValidation(func=val.val_cascade_block_x_or_f, header="x_or_f"),
    CascadeValidation(func=test_cascade_level_not_empty, header='cascade_level_not_empty'),
    CascadeValidation(func=test_valid_cascade_levels, header='cascade_level_valid_input'),
    CascadeValidation(func=val.val_matching_cascade_levels, header='cascade_level_matching')
]


@pytest.mark.parametrize("cascade_validation", cascade_validations)
def test_rtm_xlsx_cascade(fix_worksheet_columns, cascade_validation: CascadeValidation):

    # Setup
    ws_cols = fix_worksheet_columns("cascade")
    with context.worksheet_columns.set(ws_cols):
        fields = Fields()
    with context.fields.set(fields):
        work_items = WorkItems()

    # Expected result
    col_with_expected_results = cascade_validation.header
    indices_expected_to_fail = [
        index
        for index, value in enumerate(ws_cols.get_first(col_with_expected_results).body)
        if not value
    ]

    # Compare
    val_func = cascade_validation.func
    with context.fields.set(fields), context.work_items.set(work_items):
        indices_that_actually_fail = list(val_func().indices)
    assert indices_that_actually_fail == indices_expected_to_fail


def test_val_cascade_block_use_all_levels(fix_worksheet_columns):

    # Setup
    ws_cols = fix_worksheet_columns("cascade")
    with context.worksheet_columns.set(ws_cols):
        fields = Fields()
    with context.fields.set(fields):
        work_items = WorkItems()

    with context.fields.set(fields), context.work_items.set(work_items):
        assert val.val_cascade_block_use_all_columns().score == "Warning"


def test_val_matching_cascade_levels():
    pass


if __name__ == "__main__":
    pass
