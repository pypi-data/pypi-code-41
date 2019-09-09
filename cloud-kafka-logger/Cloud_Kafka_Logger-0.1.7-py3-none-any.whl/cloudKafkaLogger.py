# -*- coding: utf-8 -*-
"""Module to provide kafka handlers for internal logging facility."""

import logging
import sys
from confluent_kafka import Producer


class KafkaHandler(logging.Handler):
    """Class to instantiate the kafka logging facility."""
    def __init__(self, conf=None, topic=None):
        """Initialize an instance of the kafka handler."""
        logging.Handler.__init__(self)
        if not conf:
            sys.exit("Configuration for cloud kafka is missing")
        else:
            self.conf = conf
            try:
                self.producer = Producer(**conf)
            except Exception as e:
                sys.exit(e)
        if not topic:
            sys.exit("Please Mention the kafka topic")
        else:
            self.topic = topic

    def emit(self, record):
        """Emit the provided record to the kafka_client producer."""
        # drop kafka logging to avoid infinite recursion
        if 'kafka.' in record.name:
            return
        try:
            msg = self.format(record)
            self.producer.produce(self.topic, msg)
            self.flush(timeout=1.0)
        except Exception:
            logging.Handler.handleError(self, record)

    def flush(self, timeout=None):
        """Flush the objects."""
        self.producer.flush(timeout=1.0)

    def close(self):
        """Close the producer and clean up."""
        self.acquire()
        try:
            if self.producer:
                self.producer.close()

            logging.Handler.close(self)
        finally:
            self.release()
