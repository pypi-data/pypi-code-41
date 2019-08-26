import json
import time
import uuid

from kafka import KafkaConsumer

from glutemulo.consumer import Consumer
from glutemulo.errors import SerializerError
from glutemulo.logger import log

from .avro_utils import FastAvroDecoder


class Kafka(Consumer):
    def __init__(
        self,
        topic,
        bootstrap_servers,
        group_id=str(uuid.uuid4()),
        auto_offset_reset="earliest",
        max_poll_records=500,
        fetch_min_bytes=1000,
        **extra_consumer_params,
    ):
        self.decoder = self.get_decoder()
        self.consumer = KafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset=auto_offset_reset,
            consumer_timeout_ms=10000,  # StopIteration if no message after 10sec
            max_poll_records=max_poll_records,
            fetch_min_bytes=fetch_min_bytes,
            **extra_consumer_params,
        )

    def _consumer_generator(self):
        """Driver specific. Consumer generator
        Here we return a list of dicts"""
        while True:
            for _topic, messages in self.consumer.poll().items():
                yield (msg.value for msg in messages)

    def deserialize(self, messages, *extra_options):
        """Driver specific. Deerialize data message"""
        return (self.decoder.decode(msg) for msg in messages)

    def get_decoder(self):
        raise Exception("Implement this on subclasses!")


class JsonDecoder:
    def decode(self, msg):
        return json.loads(msg.decode("utf8"))


class JsonKafka(Kafka):
    def get_decoder(self):
        return JsonDecoder()


class AvroKafka(Kafka):
    def __init__(self, topic, schema, schema_id, **consumer_params):
        self.schema = schema
        self.schema_id = schema_id
        super().__init__(topic, **consumer_params)

    def get_decoder(self):
        return FastAvroDecoder(self.schema_id, self.schema)
