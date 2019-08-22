import datetime
import os

import numpy as np
import pandas as pd
from cached_property import cached_property

from gerby.clients import HarvestClient

from .helpers import pull_model_attributes


class Entries:
    def __init__(self, start_date=None, end_date=None):
        self.__h = HarvestClient()

        (self.start, self.end) = self.__define_date_range(start_date, end_date)

    @cached_property
    def all(self):
        return self.aggregate()

    def __define_date_range(self, start_date, end_date):
        if start_date is not None and end_date is not None:
            return (start_date, end_date)

        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        return (monday, today)

    def aggregate(self):
        entries = pd.DataFrame(
            self.__h.fetch_all("time_entries", **{"from": self.start, "to": self.end})
        )

        entries = pull_model_attributes(
            entries,
            {
                "user": ["id", "name"],
                "project": ["id", "name"],
                "client": ["id", "name"],
            },
        )
        entries = entries.drop(columns=["user", "project", "client"])
        entries = entries.rename(
            columns={
                "project_id": "harvest_project_id",
                "user_id": "harvest_user_id",
                "billable": "hours_are_billable",
            }
        )
        entries.index = entries.spent_date
        return entries

    def grouped(self):
        grouped = self.all.groupby(
            [
                "harvest_user_id",
                "hours_are_billable",
                "client_name",
                "client_id",
                "project_name",
                "harvest_project_id",
            ]
        ).sum()["hours"]
        return pd.DataFrame(grouped).reset_index()
