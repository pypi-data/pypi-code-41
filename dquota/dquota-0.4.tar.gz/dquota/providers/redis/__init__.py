import redis
import json
import os

class DQuotNotificationProviderRedis:
    def __init__(self, host = '127.0.0.1', port = 6379):
        self.redis = redis.StrictRedis(host=host,
                                       port=port,
                                       password=os.getenv('DQUOT_REDIS_PASS'))

    def send(self, input):
        notification = json.loads(input)
        self.redis.setex("quota:" + str(notification['uid']),
                         10, notification['message'])
