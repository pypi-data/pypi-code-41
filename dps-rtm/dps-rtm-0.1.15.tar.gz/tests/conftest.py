# --- Standard Library Imports ------------------------------------------------
from pathlib import Path

# --- Third Party Imports -----------------------------------------------------
import pytest

# --- Intra-Package Imports ---------------------------------------------------
from rtm.containers.fields import Fields
import rtm.main.context_managers as context
from rtm.containers.worksheet_columns import WorksheetColumns
from rtm.containers.work_items import WorkItems


# --- Worksheet Path ----------------------------------------------------------

def get_rtm_path():
    return Path(__file__).parent / "test_rtm.xlsx"


@pytest.fixture(scope="session")
def fix_path() -> Path:
    return get_rtm_path()


# --- Worksheet Columns -------------------------------------------------------

def get_worksheet_columns(worksheet_name):
    with context.path.set(get_rtm_path()):
        return WorksheetColumns(worksheet_name)


@pytest.fixture(scope="session")
def fix_worksheet_columns():
    return get_worksheet_columns


# --- Fields ------------------------------------------------------------------

def get_fields(worksheet_name):
    with context.worksheet_columns.set(get_worksheet_columns(worksheet_name)):
        return Fields()


@pytest.fixture(scope="function")
def fix_fields():
    return get_fields


# --- Work Items --------------------------------------------------------------

def get_work_items(worksheet_name):
    with context.fields.set(get_fields(worksheet_name)):
        return WorkItems()

@pytest.fixture(scope="function")
def fix_work_items():
    return get_work_items
