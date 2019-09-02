# pylint: disable=C0103
"""
Classes that wrap functions to publish to sns or consume sqs
"""
import asyncio
import inspect
import functools
import logging
import aiobotocore
from bluemax.settings import get_settings
from bluemax.utils import json_utils

LOGGER = logging.getLogger(__name__)


def stage_awair(name):
    """ prepare a stage awair name """
    stage = get_settings("stage")
    return f"{name}-{stage}"


class AwsCache:
    """ A cache for AWS clients and Sessions """

    clients = {}
    session = None
    region = None
    account_id = None

    @classmethod
    def get_endpoint_url(cls, kind):
        """ Returns endpoint url overide from settings """
        endpoint_urls = get_settings("endpoints", {})
        return endpoint_urls.get(kind)

    @classmethod
    def client(cls, kind, endpoint_url=None):
        """ Returns a cached client if available """
        client = cls.clients.get(kind)
        if client is None:
            if cls.session is None:
                loop = asyncio.get_event_loop()
                cls.session = aiobotocore.get_session(loop=loop)
            if endpoint_url is None:
                endpoint_url = cls.get_endpoint_url(kind)
            client = cls.session.create_client(kind, endpoint_url=endpoint_url)
            cls.clients[kind] = client
        return client

    @classmethod
    async def get_region_account_id(cls):
        """ returns the region and account of current credentials """
        if cls.region is None or cls.account_id is None:
            if get_settings("endpoints"):
                return "us-east-1", "123456789012"
            client = cls.client("sts")
            cls.region = client.meta.region_name
            response = await client.get_caller_identity()
            cls.account_id = response["Account"]
        return cls.region, cls.account_id

    @classmethod
    async def get_topic_arn(cls, topic):
        """
        Compose an arn from session data
        """
        region, account_id = await cls.get_region_account_id()
        topic_arn = f"arn:aws:sns:{region}:{account_id}:{topic}"
        return topic_arn

    @classmethod
    async def get_queue_url(cls, queue: str):
        """
        Returns the queue_url for queue_name
        """
        endpoint_url = cls.get_endpoint_url("sqs")
        if endpoint_url:
            # queue_url = f"{endpoint_urls['sqs']}/queue/{queue}"
            queue_url = f"http://sqs:9324/queue/{queue}"
        else:
            client = cls.client("sts")
            region = client.meta.region_name
            response = await client.get_caller_identity()
            account_id = response["Account"]
            queue_url = f"https://{region}.queue.amazonaws.com/{account_id}/{queue}"
        return queue_url

    @classmethod
    async def apublish(cls, topic_name, message):
        """ publishes a message to a topic """
        topic_arn = await cls.get_topic_arn(stage_awair(topic_name))
        return await AwsCache.client("sns").publish(TopicArn=topic_arn, Message=message)

    @classmethod
    async def apost(cls, queue_name, message):
        """ posts a message into a queue """
        queue_url = await cls.get_queue_url(stage_awair(queue_name))
        return await AwsCache.client("sqs").send_message(
            QueueUrl=queue_url, MessageBody=message
        )


def publish(topic_name, message, loop=None):
    """ returns a future from apublish """
    return asyncio.ensure_future(AwsCache.apublish(topic_name, message), loop=loop)


def post(queue_name, message, loop=None):
    """ returns a future for apost """
    return asyncio.ensure_future(AwsCache.apost(queue_name, message), loop=loop)


class aws_publish:
    """
decorator to publish to aws topic

usage::

    @aws_publish
    def foo():
        # will publish 'foo' to sns:foo
        return 'foo'

    @aws_publish(topic_name='bar')
    def foo():
        # will publish 'foo' to sns:bar
        return 'foo'
    """

    TOPICS = []

    def __init__(self, method=None, topic_name=None, loop=None):
        LOGGER.debug("__init__(%r, %r)", method, topic_name)
        if method and hasattr(method, "__call__"):
            self.method = method
            functools.update_wrapper(self, self.method)
        else:
            self.method = None
        self.topic_name = topic_name
        self.topic_arn = None
        self.loop = loop if loop else asyncio.get_event_loop()

    def __get__(self, obj, type_=None):
        return functools.partial(self, obj)

    async def _publish_(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self.method):
            document = await self.method(*args, **kwargs)
        else:
            document = self.method(*args, **kwargs)
        LOGGER.info("published %s -> %r", self.topic_name, document)
        if self.topic_arn is None:
            self.topic_arn = await AwsCache.get_topic_arn(stage_awair(self.topic_name))
        message = json_utils.dumps(document)
        LOGGER.debug("publishing: %s -> %r", self.topic_arn, message)
        try:
            response = await AwsCache.client("sns").publish(
                TopicArn=self.topic_arn, Message=message
            )
            LOGGER.debug(response)
        except Exception:
            LOGGER.exception("publishing to: %s", self.topic_arn)
            raise

    def __call__(self, *args, **kwargs):
        """ returns the task that is sending the message """
        LOGGER.debug("__call__(%r, %r) %r", args, kwargs, self.method)
        if self.method is None:
            self.method = args[0]
            functools.update_wrapper(self, self.method)
            return self
        if self.topic_name is None:
            self.topic_name = self.method.__name__
        return asyncio.ensure_future(self._publish_(*args, **kwargs), loop=self.loop)


class aws_subscribe:
    """
    decorator subscribe to aws queue

    usage::

        @aws_subscribe
        def foo(message):
            # will subscribe to sqs:foo
            print(message)

        @aws_subscribe(queue_name='bar')
        def foo(message):
            # will subscribe to sqs:bar
            print(message)
    """

    QUEUES = []

    def __init__(self, method=None, queue_name=None, loop=None):
        LOGGER.debug("__init__(%r, %r)", method, queue_name)
        if method and hasattr(method, "__call__"):
            self.method = method
            functools.update_wrapper(self, self.method)
        else:
            self.method = None
        self.queue_name = queue_name
        self.loop = loop if loop else asyncio.get_event_loop()

    def __get__(self, obj, type_=None):
        return functools.partial(self, obj)

    async def _subscribe_(self):
        sqs_client = AwsCache.client("sqs")
        queue_url = await AwsCache.get_queue_url(stage_awair(self.queue_name))
        LOGGER.info("subscribed to: %s", queue_url)
        while True:
            response = await sqs_client.receive_message(QueueUrl=queue_url)
            if "Messages" in response:
                for msg in response["Messages"]:
                    LOGGER.info("Got msg %r", msg["Body"])
                    document = msg["Body"]
                    if inspect.iscoroutinefunction(self.method):
                        asyncio.ensure_future(self.method(document))
                    else:
                        self.method(document)
                    # Need to remove msg from queue or else it'll reappear
                    await sqs_client.delete_message(
                        QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"]
                    )
            else:
                LOGGER.debug("No messages in queue")

    def __call__(self, *args, **kwargs):
        """ returns the task that listens to the queue """
        LOGGER.debug("__call__(%r, %r) %r", args, kwargs, self.method)
        if self.method is None:
            self.method = args[0]
            functools.update_wrapper(self, self.method)
            return self
        if self.queue_name is None:
            self.queue_name = self.method.__name__
        return asyncio.ensure_future(self._subscribe_(*args, **kwargs), loop=self.loop)
