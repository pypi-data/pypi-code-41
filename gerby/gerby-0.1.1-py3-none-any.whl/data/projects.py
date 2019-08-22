import os

import numpy as np
import pandas as pd
from cached_property import cached_property

from gerby.clients import ForecastClient, HarvestClient

from .helpers import pull_model_attributes


class Projects:
    def __init__(self):
        self.__h = HarvestClient()
        self.__f = ForecastClient()

    @cached_property
    def all(self):
        return self.aggregate()

    def get_all_harvest_projects(self):
        df = pd.DataFrame(self.__h.fetch_all("projects")).rename(
            columns={"id": "harvest_project_id"}
        )
        df = pull_model_attributes(df, {"client": ["id", "name"]})
        df = df[["client_id", "client_name", "name", "harvest_project_id", "is_active"]]
        return df

    def get_all_forecast_projects(self):
        df = pd.DataFrame(self.__f.projects)
        df = df.rename(
            columns={"id": "forecast_project_id", "harvest_id": "harvest_project_id"}
        )[["forecast_project_id", "name", "code", "harvest_project_id"]]
        return df

    def merge_and_sync_time_off(self, h, f):
        projects = h.merge(f, how="outer")

        projects["harvest_project_id"] = np.where(
            # conditional
            projects["forecast_project_id"] == self.__f.time_off_id,
            # if true
            self.__h.time_off_id,
            # else
            projects["harvest_project_id"],
        )

        projects["forecast_project_id"] = np.where(
            # conditional
            projects["harvest_project_id"] == self.__h.time_off_id,
            # if true
            self.__f.time_off_id,
            # else
            projects["forecast_project_id"],
        )

        dup = projects[
            np.logical_and(
                projects.forecast_project_id == self.__f.time_off_id,
                pd.isna(projects.client_id),
            )
        ].index

        projects = projects.drop(dup)

        return projects

    def aggregate(self):
        h = self.get_all_harvest_projects()
        f = self.get_all_forecast_projects()
        merged = self.merge_and_sync_time_off(h, f)
        return merged
