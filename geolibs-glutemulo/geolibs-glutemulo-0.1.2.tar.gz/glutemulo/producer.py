from glutemulo.errors import SerializerError, ProducerError


class Producer:
    def produce(self, topic, value, **options):
        message, extra_options = self.get_message_and_options(topic, value, options)
        data = self.serialize(message, **extra_options)
        return self.send(topic, data)

    def get_message_and_options(self, topic, value, options):
        """Driver specific. Serialize options and build menssage"""
        return value, options

    def serialize(self, message, *extra_options):
        """Driver specific. Serialize message to send to kafka"""
        raise SerializerError("Implement this!")

    def send(self, topic, data):
        raise ProducerError("Implement this!")
