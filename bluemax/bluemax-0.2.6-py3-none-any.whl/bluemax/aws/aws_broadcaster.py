'''
    We want multiple ECS tasks and not to have to provide
    a redis service - can aws topics and queues to the
    job
    TODO - just an idea - do not use!
'''
import asyncio
import logging
import os
from tornado.httpclient import AsyncHTTPClient
from bluemax.web.broadcaster import Broadcaster
from bluemax.utils import json_utils
from .aws_pubsub import aws_subscribe, aws_publish

LOGGER = logging.getLogger(__name__)


async def gen_queue_name():
    '''
        We need a subscription per fargate task!
        only unique this is ip address ? task arn ?
        mangle that into a name, create queue and subscriptions?
        but then how do you tidy up?
    '''
    task_uri = os.getenv('ECS_CONTAINER_METADATA_URI', None)
    if task_uri:
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch('http://www.google.com')
        except Exception:
            LOGGER.exception('Error: %s', task_uri)
            raise
        else:
            task_def = json_utils.loads(response.body)
            task_arn = task_def.get('TaskARN')
            LOGGER.info('task arn: %s', task_arn)


class AwsBroadcaster(Broadcaster):
    ''' Broadcast to topic and subscribe to queue '''

    def __init__(self, topic_name, queue_name=None):
        self.topic_name = topic_name
        self.queue_name = queue_name
        self.consumer = None
        super().__init__()

    async def broadcaster(self, queue, consumer):
        ''' Connect websockets to manager broadcast queue '''
        self.consumer = consumer
        LOGGER.info('setting up aws publisher')
        aws_publish(self._publish_, topic_name=self.topic_name)
        LOGGER.info('subscribing to aws queue')
        aws_subscribe(self.handle_broadcast, queue_name=self.queue_name)
        self.handle_broadcast()
        LOGGER.info('listening to local queue')
        while True:
            value = await queue.get()
            self._publish_(*value)
            queue.task_done()

    def _publish_(self, signal, message, client_filter=None):
        ''' will broadcast to aws the result '''
        msg = json_utils.dumps((signal, message, client_filter))
        LOGGER.debug('broadcast to aws: %s', msg)
        return msg

    async def handle_broadcast(self, message=None):
        ''' called by aws subcribe '''
        LOGGER.info('got broadcast: %s', message)
        args = json_utils.loads(message)
        asyncio.ensure_future(self.consumer(*args))
