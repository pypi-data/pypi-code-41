import json
import boto3
import pytest
from unittest.mock import patch
from moto import mock_sqs
import enervee_pipeline.config as config
from enervee_pipeline.queue_processor import QueueProcessor

TEST_INPUT_QUEUE_NAME = 'test-input-queue'
TEST_INPUT_QUEUE_URL = 'test-input-queue-url'
TEST_MESSAGE_BODY = {'product_id': 'test_id'}


def get_mocked_queue_processor(sqs, queue, queue_url, process_function, input_queue_names, should_delete_message):
    class MockQueueProcessor(QueueProcessor):
        def __init__(self, *args):
            self.conn = sqs
            self.output_queues = {TEST_INPUT_QUEUE_NAME: queue_url}
            self.input_queue_names = input_queue_names
            self.should_delete_message = should_delete_message
            self.process_function = process_function
            self.processor_id = '1234'
            self.queue = queue
            self.queue_url = queue_url

        @property
        def input_queues(self):
            input_queues = [{
                'name': TEST_INPUT_QUEUE_NAME,
                'url': queue_url,
                'queue': queue
            }]
            return input_queues

    mock_queue_processor = MockQueueProcessor(process_function, input_queue_names, should_delete_message)
    return mock_queue_processor


@pytest.fixture
@mock_sqs
def get_processor():
    def make_processor(should_delete_message=True):
        sqs_client = boto3.client('sqs', region_name=config.AWS_REGION)
        sqs_resource = boto3.resource('sqs', region_name=config.AWS_REGION)
        test_queue = sqs_resource.create_queue(QueueName=TEST_INPUT_QUEUE_NAME)
        test_queue_url = sqs_client.get_queue_url(QueueName=TEST_INPUT_QUEUE_NAME)['QueueUrl']
        sqs_client.set_queue_attributes(
            QueueUrl=test_queue_url,
            Attributes={
                'VisibilityTimeout': '0'
            }
        )
        test_processor = get_mocked_queue_processor(
            sqs=sqs_client,
            queue=test_queue,
            queue_url=test_queue_url,
            process_function=lambda x,y: True,
            input_queue_names=[TEST_INPUT_QUEUE_NAME],
            should_delete_message=should_delete_message
        )
        yield test_processor
    return make_processor


@mock_sqs
def test_publish_message(get_processor):
    processor = get_processor()
    test_processor = processor.__next__()
    test_processor.publish_message(TEST_INPUT_QUEUE_NAME, TEST_MESSAGE_BODY, {})
    response = test_processor.queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=0)
    assert response[0].body == json.dumps(TEST_MESSAGE_BODY)


@mock_sqs
def test_process_input_messages_with_deletion(get_processor):
    processor = get_processor()
    test_processor = processor.__next__()
    test_processor.publish_message(TEST_INPUT_QUEUE_NAME, TEST_MESSAGE_BODY, {})

    with patch.object(test_processor, 'process_function') as mock_process_function:
        test_processor._process_input_messages()
        remaining_messages = test_processor.queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=0)
        assert len(remaining_messages) == 0
        assert mock_process_function.call_count == 1


@mock_sqs
def test_process_input_messages_without_deletion(get_processor):
    processor = get_processor(should_delete_message=False)
    test_processor = processor.__next__()
    test_processor.publish_message(TEST_INPUT_QUEUE_NAME, TEST_MESSAGE_BODY, {})
    test_processor._process_input_messages()
    response = test_processor.queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=0)
    assert response[0].body == json.dumps(TEST_MESSAGE_BODY)


@mock_sqs
def test_get_next_input_message(get_processor):
    processor = get_processor()
    test_processor = processor.__next__()
    test_processor.publish_message(TEST_INPUT_QUEUE_NAME, TEST_MESSAGE_BODY, {})

    mocked_queue_name, mocked_queue_url, mocked_message = test_processor._get_next_input_message().__next__()
    assert mocked_queue_name == TEST_INPUT_QUEUE_NAME
    assert mocked_queue_url == test_processor.queue_url
    assert mocked_message.body == json.dumps(TEST_MESSAGE_BODY)


@mock_sqs
def test_get_next_input_message_null(get_processor):
    processor = get_processor(should_delete_message=False)
    test_processor = processor.__next__()

    null_queue_name, null_queue_url, null_message = test_processor._get_next_input_message(wait_time=0).__next__()
    assert null_queue_name is None
    assert null_queue_url is None
    assert null_message is None