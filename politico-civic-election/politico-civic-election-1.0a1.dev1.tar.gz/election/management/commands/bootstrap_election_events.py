# Imports from python.
import csv
from datetime import date
from datetime import datetime


# Imports from Django.
from django.core.management.base import BaseCommand


# Imports from other dependencies.
from geography.models import Division
import pytz
import requests
from tqdm import tqdm
import us


# Imports from election.
from election.models import ElectionCycle
from election.models import ElectionDay
from election.models import ElectionEvent


class Command(BaseCommand):
    help = (
        "Create election event instances based off "
        "current elections in the database"
    )

    base_url = (
        "https://raw.githubusercontent.com/The-Politico/"
        "election-calendar/master/2018"
    )
    data = {
        "primary_calendar": {"url": "p2018_federal.csv"},
        "reference": {"url": "state_reference.csv"},
        "primary_poll_closings": {"url": "p2018_federal_eday.csv"},
        "primary_early_voting": {"url": "p2018_federal_ev.csv"},
        "primary_registration": {"url": "p2018_federal_vr.csv"},
        "general_poll_closings": {"url": "g2018_eday.csv"},
        "general_early_voting": {"url": "g2018_ev.csv"},
        "general_registration": {"url": "g2018_vr.csv"},
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--cycle",
            action="store",
            dest="cycle",
            default="2018",
            help="Specify the election cycle you want to query against",
        )

    def handle(self, *args, **options):
        print("Loading election events")
        self.cycle, created = ElectionCycle.objects.get_or_create(
            name=options["cycle"]
        )

        for key, value in self.data.items():
            r = requests.get("{0}/{1}".format(self.base_url, value["url"]))
            reader = csv.DictReader(r.text.splitlines())
            self.data[key]["csv"] = reader

        for row in tqdm(list(self.data["reference"]["csv"])):
            if row["is_state"] == "no":
                continue

            state = row["state_code"]

            state_data = {}
            state_data["code"] = state
            state_data["name"] = us.states.lookup(row["state_code"]).name

            for key, value in self.data.items():
                for data_row in value["csv"]:
                    if state == data_row["state_code"]:
                        state_data[key] = data_row
                        break

            self.create_primaries(state_data)

            if state != "LA":
                self.create_general(state_data)

        self.create_spare_elections()

    def create_primaries(self, data):
        division = Division.objects.get(code_components__postal=data["code"])

        if data["primary_poll_closings"]["polls_close"]:
            time_zones = us.states.lookup(data["code"]).time_zones
            poll_closing_tz = "{0} {1}".format(
                data["primary_calendar"]["p2018_federal_election_date"],
                data["primary_poll_closings"]["polls_close"],
            )
            poll_closing_time = datetime.strptime(
                poll_closing_tz, "%Y-%m-%d %I:%M:%S %p"
            ).astimezone(pytz.timezone(time_zones[0]))
        else:
            poll_closing_time = None

        if data["primary_calendar"]["p2018_federal_election_date"]:
            election_day, created = ElectionDay.objects.get_or_create(
                cycle=self.cycle,
                date=data["primary_calendar"]["p2018_federal_election_date"],
            )

            ElectionEvent.objects.get_or_create(
                election_day=election_day,
                division=division,
                label="{0} {1}".format(
                    division.label, ElectionEvent.PRIMARIES
                ),
                event_type=ElectionEvent.PRIMARIES,
                dem_primary_type=self.set_null_value(
                    data["primary_calendar"].get(
                        "p2018_federal_dem_election_type"
                    )
                ),
                gop_primary_type=self.set_null_value(
                    data["primary_calendar"].get(
                        "p2018_federal_rep_election_type"
                    )
                ),
                early_vote_start=self.set_null_value(
                    data["primary_early_voting"].get(
                        "p2018_federal_evip_start_date"
                    )
                ),
                early_vote_close=self.set_null_value(
                    data["primary_early_voting"].get(
                        "p2018_federal_evip_close_date"
                    )
                ),
                vote_by_mail_application_deadline=self.set_null_value(
                    data["primary_early_voting"].get(
                        "p2018_federal_vbm_application_deadline"
                    )
                ),
                vote_by_mail_ballot_deadline=self.set_null_value(
                    data["primary_early_voting"].get(
                        "p2018_federal_ballot_return_date"
                    )
                ),
                online_registration_deadline=self.set_null_value(
                    data["primary_registration"].get(
                        "p2018_federal_online_vr_deadline"
                    )
                ),
                registration_deadline=self.set_null_value(
                    data["primary_registration"].get(
                        "p2018_federal_vr_deadline"
                    )
                ),
                poll_closing_time=poll_closing_time,
            )

        if data["primary_calendar"]["p2018_runoff_federal_election_date"]:
            election_day, created = ElectionDay.objects.get_or_create(
                cycle=self.cycle,
                date=data["primary_calendar"][
                    "p2018_runoff_federal_election_date"
                ],
            )

            ElectionEvent.objects.get_or_create(
                election_day=election_day,
                division=division,
                label="{0} {1}".format(
                    division.label, ElectionEvent.PRIMARIES_RUNOFF
                ),
                event_type=ElectionEvent.PRIMARIES_RUNOFF,
            )

    def create_general(self, data):
        division = Division.objects.get(code_components__postal=data["code"])

        if data["general_poll_closings"]["polls_close"]:
            time_zones = us.states.lookup(data["code"]).time_zones
            poll_closing_tz = "2018-11-06 {0}".format(
                data["general_poll_closings"]["polls_close"]
            )
            poll_closing_time = datetime.strptime(
                poll_closing_tz, "%Y-%m-%d %I:%M:%S %p"
            ).astimezone(pytz.timezone(time_zones[0]))
        else:
            poll_closing_time = None

        election_day, created = ElectionDay.objects.get_or_create(
            cycle=self.cycle, date=date(2018, 11, 6)
        )

        ElectionEvent.objects.get_or_create(
            election_day=election_day,
            division=division,
            label="{0} {1}".format(division.label, ElectionEvent.GENERAL),
            event_type=ElectionEvent.GENERAL,
            early_vote_start=self.set_null_value(
                data["general_early_voting"].get("g2018_evip_start_date")
            ),
            early_vote_close=self.set_null_value(
                data["general_early_voting"].get("g2018_evip_close_date")
            ),
            vote_by_mail_application_deadline=self.set_null_value(
                data["general_early_voting"].get(
                    "g2018_vbm_application_deadline"
                )
            ),
            vote_by_mail_ballot_deadline=self.set_null_value(
                data["general_early_voting"].get("g2018_ballot_return_date")
            ),
            online_registration_deadline=self.set_null_value(
                data["general_registration"].get("g2018_online_vr_deadline")
            ),
            registration_deadline=self.set_null_value(
                data["general_registration"].get("g2018_vr_deadline")
            ),
            poll_closing_time=poll_closing_time,
        )

    def set_null_value(self, val):
        if val == "":
            return None
        else:
            return val

    def create_spare_elections(self):
        new_york = Division.objects.get(code_components__postal="NY")
        ny_state_day, created = ElectionDay.objects.get_or_create(
            cycle=self.cycle, date=date(2018, 9, 13)
        )

        ElectionEvent.objects.get_or_create(
            election_day=ny_state_day,
            division=new_york,
            label="{0} {1} (state-level offices only)".format(
                new_york.label, ElectionEvent.PRIMARIES
            ),
            event_type=ElectionEvent.PRIMARIES,
            vote_by_mail_application_deadline=date(2018, 9, 6),
            vote_by_mail_ballot_deadline=date(2018, 9, 12),
            registration_deadline=date(2018, 8, 19),
        )

        georgia = Division.objects.get(code_components__postal="GA")

        ga_runoff_day_fed, created = ElectionDay.objects.get_or_create(
            cycle=self.cycle, date=date(2019, 1, 8)
        )

        ElectionEvent.objects.get_or_create(
            election_day=ga_runoff_day_fed,
            division=georgia,
            label="{0} {1} (federal offices only)".format(
                georgia.label, ElectionEvent.GENERAL_RUNOFF
            ),
            event_type=ElectionEvent.GENERAL_RUNOFF,
        )

        ga_runoff_day_state, created = ElectionDay.objects.get_or_create(
            cycle=self.cycle, date=date(2018, 12, 4)
        )

        ElectionEvent.objects.get_or_create(
            election_day=ga_runoff_day_state,
            division=georgia,
            label="{0} {1} (state offices only)".format(
                georgia.label, ElectionEvent.GENERAL_RUNOFF
            ),
            event_type=ElectionEvent.GENERAL_RUNOFF,
        )

        louisiana = Division.objects.get(code_components__postal="LA")

        la_general_day, created = ElectionDay.objects.get_or_create(
            cycle=self.cycle, date=date(2018, 12, 8)
        )

        ElectionEvent.objects.get_or_create(
            election_day=la_general_day,
            division=louisiana,
            label="{0} {1}".format(louisiana.label, ElectionEvent.GENERAL),
            event_type=ElectionEvent.GENERAL,
            early_vote_start=date(2018, 11, 24),
            early_vote_close=date(2018, 12, 1),
            vote_by_mail_application_deadline=date(2018, 12, 4),
            vote_by_mail_ballot_deadline=date(2018, 12, 7),
            online_registration_deadline=date(2018, 11, 17),
            registration_deadline=date(2018, 11, 7),
        )
