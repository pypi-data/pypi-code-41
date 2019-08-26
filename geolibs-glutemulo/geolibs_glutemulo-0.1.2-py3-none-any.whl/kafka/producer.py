import json

from glutemulo.config import config
from glutemulo.errors import ProducerError, SerializerError
from glutemulo.producer import Producer
from kafka import KafkaProducer
from kafka.errors import KafkaError

from .avro_utils import FastAvroEncoder


class Kafka(Producer):
    def __init__(self, topic=None, **producer_config):
        if not "bootstrap_servers" in producer_config:
            producer_config["bootstrap_servers"] = config["ingestor_bootstap_servers"]
        if topic is None:
            topic = config["ingestor_topic"]
        self.topic = topic
        self.producer = KafkaProducer(**producer_config)

    def produce(self, topic, value, **options):
        if topic is None:
            topic = self.topic
        return super().produce(topic, value, **options)

    def send(self, topic, serialized_data):
        try:
            return self.producer.send(topic, serialized_data)
        except KafkaError as error:
            raise ProducerError(f"Kafka error: {error.args[0]}")


class JsonKafka(Kafka):
    def serialize(self, message):
        return json.dumps(message).encode("utf-8")


class AvroKafka(Kafka):
    """
        Kafka Producer client which does avro schema encoding to messages.
        Handles schema registration, Message serialization.
        Constructor takes below parameters.
        :param str default_value_schema: Optional default avro schema for value
        :param int value_schema_id: Optional default schema id (if None register it as value schema)
        :param str topic: Topic (for schema registration)
    """

    def __init__(
        self,
        default_value_schema=None,
        value_schema_id=None,
        topic=None,
        **producer_config,
    ):
        self.value_schema = default_value_schema
        self.value_schema_id = value_schema_id
        self.encoders = {}  # schema_id to encoder object
        super().__init__(topic, **producer_config)

    def get_message_and_options(self, topic, value, options):
        """Clean kwargs al get data to serialize and send"""
        options = dict(
            schema=options.get("schema", self.value_schema),
            topic=options.get("topic", topic or self.topic),
        )
        return value, options

    def serialize(self, message, schema=None, topic=None):
        if not topic:
            raise ProducerError("Topic name not specified.")

        if not schema:
            raise SerializerError("Avro schema required for values")
        return self._encode_record_with_schema(topic, schema, message)

    def _encode_record_with_schema(self, topic, schema, record):
        """
        Given a parsed avro schema, encode a record for the given topic.  The
        record is expected to be a dictionary.
        The schema is registered with the subject of 'topic-value'
        :param str topic: Topic name
        :param schema schema: Avro Schema
        :param dict record: An object to serialize
        :returns: Encoded record with schema ID as bytes
        :rtype: bytes
        """

        # get the latest schema for the subject
        subject = topic + "-value"
        # register it
        schema_id = self.register(subject, schema)
        if not schema_id:
            message = "Unable to retrieve schema id for subject %s" % (subject)
            raise SerializerError(message)

        # cache writer
        if schema_id not in self.encoders:
            self.encoders[schema_id] = FastAvroEncoder(schema, schema_id)
        return self.encoders[schema_id].encode(record)

    def register(self, subject, schema):
        """For register in schema registry if necessary and return schema id"""
        if self.value_schema_id:
            return self.value_schema_id
        # TODO: Register and get id in a schema registry
