import datetime
import os

import numpy as np
import pandas as pd
from cached_property import cached_property

from gerby.clients import ForecastClient
from gerby.constants import HOURS_PER_DAY, SECONDS_PER_DAY


class Assignments:
    def __init__(self, start_date=None, end_date=None):
        self.__f = ForecastClient()
        (self.start, self.end) = self.__define_date_range(start_date, end_date)

    @cached_property
    def all(self):
        return self.get_assignments()

    def __define_date_range(self, start_date, end_date):
        if start_date is not None and end_date is not None:
            return (start_date, end_date)

        today = datetime.date.today()
        sunday = today - datetime.timedelta(days=(today.weekday() + 1))
        saturday = sunday + datetime.timedelta(days=6)
        return (sunday, saturday)

    def annotate(self, assignments_df):
        df = assignments_df.copy()
        df["start_date"] = pd.to_datetime(df["start_date"])
        df["allocation"] = df["allocation"].fillna(SECONDS_PER_DAY)
        df = df.assign(
            n_days=lambda x: (
                (pd.to_datetime(x["end_date"]) - pd.to_datetime(x["start_date"]))
                / np.timedelta64(1, "D")
                + 1
            ),
            hours_per_day=lambda x: x["allocation"] / 60 / 60,
        )
        df["work_week"] = df["start_date"] - pd.to_timedelta(
            df["start_date"].dt.dayofweek, unit="d"
        )

        df = df.reset_index(drop=True)
        # round up hours per day to full day
        df = df.assign(
            hours_per_day=np.where(
                df["hours_per_day"] > HOURS_PER_DAY * 0.75,
                HOURS_PER_DAY,
                df["hours_per_day"],
            )
        )
        df["forecasted_hours"] = df["n_days"] * df["hours_per_day"]
        return df

    def get_assignments(self):
        assignments = self.__f.assignments(self.start.isoformat(), self.end.isoformat())
        df = pd.DataFrame(assignments["assignments"])
        df = df.rename(
            columns={
                "person_id": "forecast_user_id",
                "project_id": "forecast_project_id",
            }
        )
        return self.annotate(df)

    def grouped_by_week(self):
        df = self.all
        df = pd.DataFrame(
            df.groupby(["work_week", "forecast_user_id", "forecast_project_id"]).sum()[
                "forecasted_hours"
            ]
        ).reset_index()
        return df

    def grouped(self):
        df = self.all
        df = pd.DataFrame(
            df.groupby(["forecast_user_id", "forecast_project_id"]).sum()[
                "forecasted_hours"
            ]
        ).reset_index()
        return df
