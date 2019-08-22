import os

import numpy as np
import pandas as pd
from cached_property import cached_property

from gerby.clients import ForecastClient, HarvestClient, SlackClient


class Users:
    def __init__(self):
        self.__h = HarvestClient()
        self.__f = ForecastClient()
        self.__s = SlackClient()

    @cached_property
    def all(self):
        return self.aggregate()

    def __get_email_from_slack_user(self, row):
        if "email" in row["profile"].keys():
            return row["profile"]["email"]
        else:
            return None

    def get_all_slack_users(self):
        # get all the users
        users_info = self.__s.api_call("users.list")
        # cram into dataframe
        df = pd.DataFrame(users_info["members"])
        # keep only those we care about
        team_members = df[
            np.logical_and(df["is_restricted"] == False, df["is_bot"] == False)
        ]
        # pull the email from the profile
        team_members = team_members.assign(
            email=team_members.apply(self.__get_email_from_slack_user, axis=1)
        )[["real_name", "email", "id", "name"]]
        # keep those that have emails (bye bye slackbot)
        team_members = team_members[pd.isnull(team_members["email"]) == False]
        # rename id to slack id
        team_members = team_members.rename(
            columns={"id": "slack_user_id", "name": "slack_handle"}
        )
        return team_members

    def get_all_forecast_users(self):
        df = pd.DataFrame(self.__f.people)
        df = df[df["archived"] != True][["email", "id", "harvest_user_id"]]
        df = df.rename(columns={"id": "forecast_user_id"})[
            ["email", "forecast_user_id", "harvest_user_id"]
        ]
        return df

    def get_all_harvest_users(self):
        # fetch all from harvest
        df = pd.DataFrame(self.__h.fetch_all("users"))
        # rename our columns appropriately
        df = df.rename(columns={"id": "harvest_user_id"})
        df = df[df["is_active"]]
        df = df.assign(billable=df["roles"].apply(lambda x: "Billable" in x))
        df = df.assign(engineer=df["roles"].apply(lambda x: "Engineer" in x))
        df = df.assign(designer=df["roles"].apply(lambda x: "UI/UX design" in x))
        df = df.assign(pm=df["roles"].apply(lambda x: "Product Manager" in x))
        df = df.assign(check_daily=np.logical_or(df["engineer"], df["designer"]))
        df = df.assign(check_weekly=df["billable"])
        return df

    def aggregate(self):
        slack_users = self.get_all_slack_users()
        harvest_users = self.get_all_harvest_users()
        forecast_users = self.get_all_forecast_users()
        return slack_users.merge(harvest_users, how="left").merge(
            forecast_users, how="left"
        )
