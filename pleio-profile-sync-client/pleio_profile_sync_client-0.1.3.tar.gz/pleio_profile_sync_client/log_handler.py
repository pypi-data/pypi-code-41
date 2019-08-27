import uuid
from logging import StreamHandler


# HTTPLogHandler is a logging.StreamHandler that posts logs through HTTP
class HTTPLogHandler(StreamHandler):
    def __init__(self, client, *args, **kwargs):
        self.client = client
        self.uuid = uuid.uuid4()
        super().__init__(*args, **kwargs)

    def emit(self, record):
        self.client.post_log({
            'uuid': str(self.uuid),
            'content': self.format(record)
        })
