# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.containers.worksheet_columns as wc
import rtm.main.context_managers as context


def test_ws_cols_init(fix_path):
    with context.path.set(fix_path):
        worksheet_columns = wc.WorksheetColumns("test_worksheet")
    for ws_col in worksheet_columns:
        assert isinstance(ws_col, wc.WorksheetColumn)


if __name__ == "__main__":
    pass
