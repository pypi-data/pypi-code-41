import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


async def rabbitmq_bind_subscribe_key_to_topic(broker_handler, subscribe_key_list, topic_list=None):
    '''
    用routing_key将queue和topic绑定起来
    :param subscribe_key_list: 需要订阅的key list
    :param topic_list: 绑定的topic list
    :return:
    '''

    await broker_handler.bind_routing_key(subscribe_key_list, topic_list)
    logging.info('bind subscribe_key%s to topic%s success', subscribe_key_list, topic_list)


async def rabbitmq_unbind_subscribe_key_to_topic(broker_handler, subscribe_key_list, topic_list=None):
    '''
    用routing_key将queue和topic解除绑定
    :param subscribe_key_list: 需要解除订阅的key list
    :param topic_list: topic list
    :return:
    '''

    await broker_handler.unbind_routing_key(subscribe_key_list, topic_list)
    logging.info('unbind subscribe_key%s to topic%s success', subscribe_key_list, topic_list)


async def listening_message(broker_handler):
    await broker_handler.listening_message()
