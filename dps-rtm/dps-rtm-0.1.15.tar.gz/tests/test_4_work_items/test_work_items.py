# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.context_managers as context
import rtm.containers.fields
from rtm.containers.work_items import WorkItems


def test_work_items(fix_worksheet_columns):

    # --- Extract data from worksheet -----------------------------------------
    ws_cols = fix_worksheet_columns("cascade")
    with context.worksheet_columns.set(ws_cols):
        fields = rtm.containers.fields.Fields()
    # position_should = list(ws_cols.get_first('position').body)
    parents_should = list(ws_cols.get_first('parent').body)

    # --- Initializes work items ----------------------------------------------
    with context.fields.set(fields):
        work_items = WorkItems()

    # # --- Check Position ------------------------------------------------------
    # position_actual = [item.position for item in work_items]
    # assert position_actual == position_should

    # --- Check Parent --------------------------------------------------------
    parents_actual = [item.parent for item in work_items]
    assert parents_actual == parents_should


def test_work_item_index_count(fix_fields):
    fields = fix_fields("cascade")
    assert fields.body_length == 25
