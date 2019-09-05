import json
import snowplow_tracker
import time
from snowplow_tracker import logger
from snowplow_tracker import SelfDescribingJson
from snowplow_tracker import Subject, Tracker, Emitter


class SnowplowManager:
    def __init__(self, config):
        """
        Initialize service
        """
        with open('src/config.json') as config_file:
            self.defaultConfig = json.load(config_file)
        self.companyConfig = config
        self.tracker = None
        self.emitter = None
        self.subject = None

    def setup_tracker(self):
        """Setup an instance of a tracker"""
        self.companyConfig = self.setup_config(self.companyConfig)
        self.emitter = Emitter(
            self.companyConfig["COLLECTOR_HOST"],
            protocol = self.companyConfig["PROTOCOL"],
            port = self.companyConfig["PORT"],
            method = self.companyConfig["EMIT_METHOD"],
            buffer_size = self.companyConfig["BUFFER_SIZE"]
        )
        self.subject = Subject()
        self.tracker = Tracker(
            emitters = self.emitter,
            subject = self.subject,
            namespace = self.companyConfig["TRACKER_NAME"],
            app_id = self.companyConfig["APP_ID"],
            encode_base64 = self.companyConfig["ENCODE64"]
        )

        return self.tracker

    def setup_config(self, config):
        """Setup config with company and default config"""
        if config['TRACKER_NAME'] is None or \
            config['APP_ID'] is None:
            return

        keys = [
            'COLLECTOR_HOST',
            'PROTOCOL',
            'EMIT_METHOD',
            'BUFFER_SIZE',
            'DEBUG_MODE',
            'ENCODE64',
            'PORT'
        ]

        for key in keys:
            config[key] = self.defaultConfig[key]

        if "DEV_ENV" in config:
            if config["DEV_ENV"] == True:
                config["COLLECTOR_HOST"] = self.defaultConfig["COLLECTOR_HOST_DEV"]

        if "INSPETOR_ENV" in config:
            if config["INSPETOR_ENV"] == True:
                config["COLLECTOR_HOST"] = 'test'

        return config

    def track_describing_event(self, schema, data, context, action) :
        """ Track describing snowplow event """
        self.tracker.track_self_describing_event(
                SelfDescribingJson(
                    schema,
                    data
                ),
                [
                    SelfDescribingJson(
                        context,
                        {
                            'action': action
                        }
                    ),
                ],
                self.get_normalized_timestamp()
            )

    def track_non_describing_event(self, schema) :
        """ Track non describing snowplow event """
        self.tracker.track_self_describing_event(
            SelfDescribingJson(
                self.defaultConfig["INGRESSE_SERIALIZATION_ERROR"],
                {
                    'intendedSchemaId': schema
                }
            ),
            [],
            self.get_normalized_timestamp()
        )

    def flush(self):
        """
        Flush trackers
        """
        self.tracker.flush()

    def get_normalized_timestamp(self):
        """
        Get correct timestamp
        """
        return int(time.time())*1000

    def get_normalized_data(self, data):
        """
        Format string to replace non-ascii characters
        """
        return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore').decode('utf-8')
