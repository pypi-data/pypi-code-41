import array as arr
import json
import os
import unicodedata

from src.inspetor.model.inspetor_abstract_model import InspetorAbstractModel
from src.inspetor.inspetor_json_encoder import AbstractModelEncoder
from src.inspetor.exception.tracker_exception import TrackerException

from src.snowplow_manager import SnowplowManager

class InspetorResource:
    def __init__(self, config_dict):
        """
        Initialize service
        """
        with open('src/config.json') as config_file:
            self.defaultConfig = json.load(config_file)
        self.tracker = None
        self.snowplowManager = SnowplowManager(config_dict)
        self.verify_tracker()

    def verify_tracker(self):
        """Verify if tracker already exists"""
        if self.tracker is None:
            self.tracker = self.snowplowManager.setup_tracker()

        return True

    def track_described_event(
        self,
        schema,
        data,
        context = None,
        action = None
    ):
        """
        Track a described event

        Keyword Arguments:
        schema     -- string
        data       -- array
        context    -- string
        action     -- string
        """
        self.verify_tracker()
        try:
            data = data.jsonSerialize()
        except Exception as encoder_fail:
            self.report_non_descriptible_call(schema)
            return False

        self.snowplowManager.track_describing_event(schema, data, context, action)

    def report_non_descriptible_call(self, schema):
        """
        Track a non described event

        Keyword Arguments:
        schema     -- string
        """
        self.verify_tracker()

        self.snowplowManager.track_non_describing_event(schema)

    def track_account_action(self, data, action):
        """
        Track an Account action

        Keyword Arguments:
        data       -- InspetorAccount
        action     -- string
        """

        valid_actions = [
            "account_create",
            "account_update",
            "account_delete"
        ]

        if not action in valid_actions:
            raise TrackerException(
                TrackerException.INVALID_ACCOUNT_CONTEXT
            )

        if action == "account_create":
            data.is_valid()

        data.is_valid_update()

        self.track_described_event(
            self.defaultConfig["INSPETOR_ACCOUNT_SCHEMA"],
            data,
            self.defaultConfig["INSPETOR_CONTEXT_SCHEMA"],
            action
        )

    def track_sale_action(self, data, action):
        """
        Track a Sale action

        Keyword Arguments:
        data       -- InspetorSale
        action     -- string
        """

        valid_actions = [
            "sale_create",
            "sale_update"
        ]

        if not action in valid_actions:
            raise TrackerException(
                TrackerException.INVALID_SALE_CONTEXT
            )

        if action == "sale_create":
            data.is_valid()
        else:
            data.is_valid_update()

        self.track_described_event(
            self.defaultConfig["INSPETOR_SALE_SCHEMA"],
            data,
            self.defaultConfig["INSPETOR_CONTEXT_SCHEMA"],
            action
        )

    def track_event_action(self, data, action):
        """
        Track an Event action

        Keyword Arguments:
        data       -- InspetorEvent
        action     -- string
        """

        valid_actions = [
            "event_create",
            "event_update",
            "event_delete"
        ]

        if not action in valid_actions:
            raise TrackerException(
                TrackerException.INVALID_EVENT_CONTEXT
            )

        if action == "event_create":
            data.is_valid()

        data.is_valid_update()

        self.track_described_event(
            self.defaultConfig["INSPETOR_EVENT_SCHEMA"],
            data,
            self.defaultConfig["INSPETOR_CONTEXT_SCHEMA"],
            action
        )

    def track_item_transfer_action(self, data, action):
        """
        Track an ItemTransfer action

        Keyword Arguments:
        data       -- ItemTransfer
        action     -- string
        """

        valid_actions = [
            "item_transfer_create",
            "item_transfer_update_status"
        ]

        if not action in valid_actions:
            raise TrackerException(
                TrackerException.INVALID_TRANSFER_CONTEXT
            )

        if action == "transfer_create":
            data.is_valid()

        data.is_valid_update()

        self.track_described_event(
            self.defaultConfig["INSPETOR_TRANSFER_SCHEMA"],
            data,
            self.defaultConfig["INSPETOR_CONTEXT_SCHEMA"],
            action
        )

    def track_account_auth_action(self, data, action):
        """
        Track an AccountAuth action

        Keyword Arguments:
        data       -- AccountAuth
        action     -- string
        """

        valid_actions = [
            "account_login",
            "account_logout"
        ]

        if not action in valid_actions:
            raise TrackerException(
                TrackerException.INVALID_AUTH_CONTEXT
            )

        data.is_valid()

        self.track_described_event(
            self.defaultConfig["INSPETOR_AUTH_SCHEMA"],
            data,
            self.defaultConfig["INSPETOR_CONTEXT_SCHEMA"],
            action
        )

    def track_password_recovery_action(self, data, action):
        """
        Track an PasswordRecovery action

        Keyword Arguments:
        data       -- PasswordRecovery
        action     -- string
        """

        valid_actions = [
            "password_reset",
            "password_recovery"
        ]

        if not action in valid_actions:
            raise TrackerException(
                TrackerException.INVALID_PASS_CONTEXT
            )

        data.is_valid()

        self.track_described_event(
            self.defaultConfig["INSPETOR_PASS_RECOVERY_SCHEMA"],
            data,
            self.defaultConfig["INSPETOR_CONTEXT_SCHEMA"],
            action
        )
