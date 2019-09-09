import json
from multiprocessing import Process
from enervee_pipeline.utils.queue import get_sqs_conn, get_sqs_queue, enqueue_message
from enervee_pipeline.utils.string import get_uuid
from enervee_pipeline import config
import logging

LOGGER = logging.getLogger(config.LOGGER_NAME)
DEFAULT_WAIT_TIME_IN_SECONDS = 20

class QueueProcessor(Process):

    def __init__(self, processor_function, input_queue_names, should_delete_message=False):
        """
        Constructs a new QueueProcessor.
        :param function processor_function: function that does work using message data and ID
        :param list[str] input_queue_names: names of queue
        :param bool should_delete_message: should delete queue message after process_function successfully completes
        """
        super(QueueProcessor, self).__init__()
        self.processor_id = get_uuid()
        self.process_function = processor_function
        self.should_delete_message = should_delete_message
        self.conn = get_sqs_conn()
        self.input_queue_names = input_queue_names
        self.output_queues = dict()

    @property
    def input_queues(self):
        input_queues = []
        for queue_name in self.input_queue_names:
            queue, queue_url = get_sqs_queue(self.conn, queue_name)
            input_queue = {
                'name': queue_name,
                'url': queue_url,
                'queue': queue
            }
            input_queues.append(input_queue)
        return input_queues

    def run(self):
        """
        Run loop for the processor to process queue messages. Fetches the next message from the next input queue,
        then processes it using the passed in process_function.
        """
        self.initialize()
        LOGGER.info('Starting processor: %s' % self.processor_id)
        while True:
            self._process_input_messages()

    def initialize(self):
        pass

    def _process_input_messages(self, wait_time=DEFAULT_WAIT_TIME_IN_SECONDS):
        for queue_name, queue_url, message in self._get_next_input_message(wait_time):
            if message is not None:
                message_id = message.message_id
                message_body = json.loads(message.body)
                LOGGER.info('Processing queue: %s, processor: %s, message: %s' % (queue_name, self.processor_id, message_id))
                self.process_function(message_body, message_id)
                LOGGER.info('Finished processing queue: %s, processor: %s, message: %s' % (queue_name, self.processor_id, message_id))
                if self.should_delete_message:
                    self.conn.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message.receipt_handle
                    )

    def _get_next_input_message(self, wait_time=DEFAULT_WAIT_TIME_IN_SECONDS):
        for input_queue in self.input_queues:
            queue = input_queue['queue']
            queue_name = input_queue['name']
            queue_url = input_queue['url']
            queue_messages = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=wait_time)

            if len(queue_messages) > 0:
                message = queue_messages[0]
                yield queue_name, queue_url, message
        yield None, None, None

    def publish_message(self, queue_name, message_body, message_attributes={}):
        """
        Publishes a message to an output queue.
        :param str queue_name: name of queue
        :param dict message_body: Any JSON serializable data
        :param dict message_attributes: (optional) Metadata to configure SQS message attr
        """
        if queue_name not in self.output_queues:
            output_queue, output_queue_url = get_sqs_queue(self.conn, queue_name)
            self.output_queues[queue_name] = output_queue_url
        queue_url = self.output_queues[queue_name]
        enqueue_message(self.conn, queue_url, message_body, message_attributes)
