async def rabbitmq_publish_one(broker_handler, key=None, data=None, topic=None):
    '''

    :param broker_handler:
    :param key:
    :param data:
    :param topic:
    :return:
    '''
    await broker_handler.publish_message(key, data, topic)
