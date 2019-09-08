import pandas as pd
import numpy as np

from seeq.sdk import *

from .. import _common
from .. import _login


def pull(workbooks):
    workbooks_api = WorkbooksApi(_login.client)

    for index, row in workbooks.iterrows():
        if not _common.present(row, 'ID'):
            raise RuntimeError('All rows in "workbooks" argument must have valid "ID" column')

        workbook_output = workbooks_api.get_workbook(id=row['ID'])  # type: WorkbookOutputV1
