import time

from glutemulo.errors import SerializerError


class Consumer:

    def consume(self, wait_interval=0):
        while True:
            for msg in self._consumer_generator():
                yield self.deserialize(msg)
                time.sleep(wait_interval)

    def _consumer_generator(self):
        """Driver specific. Consumer generator"""
        raise SerializerError("Implement this!")

    def deserialize(self,  message, *extra_options):
        """Driver specific. Deerialize data message"""
        raise SerializerError("Implement this!")
