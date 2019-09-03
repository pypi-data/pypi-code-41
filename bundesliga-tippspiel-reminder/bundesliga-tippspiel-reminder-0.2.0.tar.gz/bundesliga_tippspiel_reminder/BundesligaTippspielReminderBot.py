"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of bundesliga-tippspiel-reminder (btr).

btr is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

btr is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with btr.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from bokkichat.entities.message.TextMessage import TextMessage
from kudubot.Bot import Bot
from kudubot.db.Address import Address as Address
from kudubot.parsing.CommandParser import CommandParser
from bundesliga_tippspiel_reminder.db.ApiKey import ApiKey
from bundesliga_tippspiel_reminder.db.Reminder import Reminder
from bundesliga_tippspiel_reminder.BundesligaTippspielReminderParser import \
    BundesligaTippspielReminderParser
from bundesliga_tippspiel_reminder.api import api_request, api_is_authorized


class BundesligaTippspielReminderBot(Bot):
    """
    The bundesliga tippspiel reminder bot
    """

    def on_command(
            self,
            message: TextMessage,
            parser: CommandParser,
            command: str,
            args: Dict[str, Any],
            sender: Address,
            db_session: Session
    ):
        """
        Defines the behaviour of the bot when receiving a message
        :param message: The received message
        :param parser: The parser that matched the message
        :param command: The command that matched the message
        :param args: The arguments of the command
        :param sender: The sender of the message
        :param db_session: The database session to use
        :return: None
        """
        if command == "login":
            self._handle_login(sender, args, db_session)
            return
        elif command == "is_authorized":
            self._handle_is_authorized(sender, db_session)
            return

        # Everything beyond this requires authorization
        api_key = self._get_api_key(sender, db_session)
        if api_key is None:
            self.connection.send(TextMessage(
                self.connection.address,
                sender,
                "Not authorized, use /login <username> <password> first",
                "Not authorized"
            ))
            return

        reminder = self._get_reminder(sender, db_session)
        if command == "leaderboard":
            self._handle_leaderboard(sender, api_key)
        elif command == "reminder_state":
            self._handle_reminder_state(sender, reminder)
        elif command == "activate_reminder":
            self._handle_activate_reminder(sender, args, reminder, db_session)
        elif command == "deactivate_reminder":
            self._handle_deactivate_reminder(sender, reminder, db_session)

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the bot
        """
        return "bundesliga-tippspiel-reminder"

    @classmethod
    def parsers(cls) -> List[CommandParser]:
        """
        :return: The parsers for the bot
        """
        return [BundesligaTippspielReminderParser()]

    @classmethod
    def extra_config_args(cls) -> List[str]:
        """
        :return: A list of additional settings parameters required for
                 this bot. Will be stored in a separate extras.json file
        """
        return []

    @staticmethod
    def _get_api_key(address: Address, db_session: Session) \
            -> Optional[str]:
        """
        Retrieves the API key for an address
        :param address: The address for which to get the API key
        :param db_session: The database session to use
        :return: The API key, or None if no API key exists
        """
        api_key = db_session.query(ApiKey).filter_by(kudubot_user=address)\
            .first()
        return None if api_key is None else api_key.key

    @staticmethod
    def _get_reminder(address: Address, db_session: Session) \
            -> Optional[Reminder]:
        """
        Retrieves the reminder object for a user from the database
        :param address: The address of the user
        :param db_session: The database session to use
        :return: The Reminder object or None if none exist.
        """
        return db_session.query(Reminder).filter_by(kudubot_user=address)\
            .first()

    def _handle_login(
            self,
            sender: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles a login command
        :param sender: The sender of the message
        :param args: The command arguments
        :param db_session: The database session
        :return: None
        """

        data = {"username": args["username"], "password": args["password"]}
        response = api_request("api_key", "post", data)

        if response["status"] == "ok":
            key = ApiKey(
                kudubot_user=sender,
                tippspiel_user=args["username"],
                key=response["data"]["api_key"]
            )
            db_session.add(key)
            db_session.commit()
            reply = "Logged in successfully"
        else:
            reply = "Login unsuccessful"

        reply = TextMessage(self.connection.address, sender, reply, "Login")
        self.connection.send(reply)

    def _handle_is_authorized(self, sender: Address, db_session: Session):
        """
        Handles an is_authorized command
        :param sender: The sender of the message
        :param db_session: The database session to use
        :return: None
        """
        api_key = self._get_api_key(sender, db_session)
        reply = "yes" if api_is_authorized(api_key) else "no"
        self.connection.send(TextMessage(
            self.connection.address, sender, reply, "Authorized"
        ))

    def _handle_leaderboard(self, sender: Address, api_key: str):
        """
        Handles a leaderboard command
        :param sender: The sender of the message
        :param api_key: The API key to use
        :return: None
        """
        response = api_request("leaderboard", "get", {}, api_key)

        if response["status"] == "ok":
            leaderboard = response["data"]["leaderboard"]
            formatted = []
            for i, (user, points) in enumerate(leaderboard):
                formatted.append("{}: {} ({})".format(
                    i + 1,
                    user["username"],
                    points
                ))

            reply = "\n".join(formatted)
            self.connection.send(TextMessage(
                self.connection.address, sender, reply, "Leaderboard"
            ))

    def _handle_reminder_state(
            self,
            sender: Address,
            reminder: Optional[Reminder]
    ):
        """
        Handles a reminder_state command
        :param sender: The sender of the command
        :param reminder: The reminder for that user
        :return: None
        """
        if reminder is None:
            reply = "No reminder set"
        else:
            reply = "Reminder set to go off {} hours before a match.".format(
                int(reminder.reminder_time / 3600)
            )
        self.connection.send(TextMessage(
            self.connection.address, sender, reply, "Reminder State"
        ))

    def _handle_activate_reminder(
            self,
            sender: Address,
            args: Dict[str, Any],
            reminder: Optional[Reminder],
            db_session: Session
    ):
        hours = args["hours"]
        seconds = hours * 3600
        if hours < 1 or hours > 120:
            self.connection.send(TextMessage(
                self.connection.address, sender,
                "Reminders can only be 1-120 hours", "Invalid Reminder Time"
            ))
            return

        if reminder is None:
            reminder = Reminder(
                kudubot_user=sender,
                reminder_time=seconds
            )
            db_session.add(reminder)
        else:
            reminder.reminder_time = seconds

        db_session.commit()

        self.connection.send(TextMessage(
            self.connection.address, sender,
            "Reminder set to {} hours".format(hours), "Reminder Time set"
        ))

    def _handle_deactivate_reminder(
            self,
            sender: Address,
            reminder: Optional[Reminder],
            db_session: Session
    ):
        """
        Deactivates a reminder
        :param sender: The sender of the message
        :param reminder: The previously existing reminder
        :param db_session: The database session to use
        :return: None
        """
        if reminder is not None:
            db_session.delete(reminder)
            db_session.commit()
        self.connection.send(TextMessage(
            self.connection.address, sender,
            "Reminder Deactivated", "Reminder Deactivated"
        ))

    def run_in_bg(self):
        """
        Background thread that periodically checks if any reminders are due
        :return: None
        """
        self.logger.info("Starting background thread")
        while True:
            self.logger.info("Checking for due reminders")

            db_session = self.sessionmaker()
            matches = None  # Refresh matches each iteration

            for reminder in db_session.query(Reminder).all():
                api_key = self._get_api_key(reminder.kudubot_user, db_session)

                if not api_is_authorized(api_key):
                    continue

                if matches is None:
                    resp = api_request("match", "get", {}, api_key)
                    matches = resp["data"]["matches"]
                bets = api_request("bet", "get", {}, api_key)["data"]["bets"]
                due = reminder.get_due_matches(matches, bets)

                if len(due) > 0:
                    body = "Reminders for hk-tippspiel.com:\n\n"
                    for match in due:
                        body += "{} vs. {}\n".format(
                            match["home_team"]["name"],
                            match["away_team"]["name"]
                        )
                    msg = TextMessage(
                        self.connection.address,
                        reminder.kudubot_user,
                        body,
                        "Reminders"
                    )
                    self.connection.send(msg)
                    last_match = max(due, key=lambda x: x["kickoff"])
                    reminder.last_reminder = last_match["kickoff"]
                    db_session.commit()

            self.logger.info("Finished checking for due reminders")
            self.sessionmaker.remove()
            time.sleep(3600)
