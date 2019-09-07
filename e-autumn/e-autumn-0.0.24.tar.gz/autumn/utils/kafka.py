from confluent_kafka import Producer, Consumer, TopicPartition, KafkaError
from loguru import logger
import time
import json
import random

def check_builtin_condition(key, now, end):
    if key == "depth":
        if now > end:
            return False
        else:
            return True
    elif key == "create_at":
        if time.time() - int(now) > int(end):
            return False
        else:
            return True

class KafkaError(Exception):
    pass


class KafkaSender:
    def __init__(self, servers: str, flush_timeout=10):
        """
        Init a kafka sender
        :param servers: (str)bootstrap.servers
        :param flush_timeout: (int)Timeout for flush message
        """
        self.servers = servers
        self.message_list = []
        self.flush_timeout = flush_timeout

    def add_message(self, topic: str, message, partition=None):
        """
        Add a message to the waiting queue
        :param topic: (str) the topic of the message
        :param message: (dict, list, str, bytes) the body of message
        :param partition: (int) the partition of the sending topic, default means random
        """
        if type(message) == dict or type(message) == list:
            msg = json.dumps(message).encode()
        elif type(message) == str:
            msg = message.encode()
        elif type(message) == bytes:
            msg = message
        else:
            raise TypeError("Unsupported type :" + type(message))
        self.message_list.append((topic, partition, msg))
        return

    def send_all(self) -> (bool, str):
        """
        Send all messages in waiting queue
        :return: (status, error_message)
        """
        if len(self.message_list) == 0:
            return True, "No available message"
        producer = Producer({'bootstrap.servers': self.servers})
        for message in self.message_list:
            producer.produce(topic=message[0], value=message[2], partition=message[1])
            producer.poll(0)
        producer.flush(self.flush_timeout)
        # producer.length == 0 means that all the messages have been sent.
        if len(producer) == 0:
            self.message_list = []
            return True, ""
        else:
            l1 = len(self.message_list)
            l2 = len(producer)
            self.message_list = []
            return False, "Not all messages has been sent. Sent(%d/%d)" % (l1 - l2, l1)


class KafkaConsumer(Consumer):
    def __init__(self, servers: str, topics: list, group: str):
        """
        Init a kafka consumer
        :param servers: (str)bootstrap.servers
        :param topics: (str)group.id
        :param group: (list of str)subscribe topics
        """
        super().__init__({
            'bootstrap.servers': servers,
            'group.id': 'autumn',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })
        self.subscribe(topics)

    def __del__(self):
        self.close()

    def clear_assignment(self):
        """
        Clear all assignment
        """
        self.assign([])

    def add_assignment(self, topic, partition, offset):
        """
        Add a assignment
        :param topic: (str) Assignment topic
        :param partition: (int) Assignment partition
        :param offset: (int) Assignment offset
        """
        p = TopicPartition(topic=topic, partition=partition, offset=offset)
        self.assign(self.assignment() + [p])

    def remove_assignment(self, topic, partition, offset):
        """
        remove a assignment
        :param topic: (str) Assignment topic
        :param partition: (int) Assignment partition
        :param offset: (int) Assignment offset
        """
        self.assign(self.assignment().remove(TopicPartition(topic=topic, partition=partition, offset=offset)))

    def poll(self):
        """
        Poll a message
        :return: (confluent_kafka.Message) Kafka message
        """
        while True:
            message = super().poll(5)
            if message is None:
                continue
            if message.error():
                if message.error().code() == -191:
                    time.sleep(1)
                    continue
                raise KafkaError(message.error())
            return message


class KafkaMonitor(KafkaConsumer):
    def __init__(self, executor):
        """
        Init a kafka monitor
        :param kafka_url: kafka urls
        :param topic: kafka_topic
        :param group: kafka_group
        :param arrangement: the partition&offset arrangement to sync
        """
        self.executor=executor
        logger.debug(id(self.executor))
        super().__init__(executor.kafka_url, [executor.kafka_topic], executor.kafka_group)
        self.clear_assignment()
        self.topic = executor.kafka_topic

    def poll(self):
        """
        Get a new message
        :return: confluent_kafka.Message
        """
        while True:
            # 出现了新的分配/再平衡
            temp = None
            while True:
                try:
                    temp = self.executor.queue.get_nowait()
                    print("tempppppp", temp)
                except:
                    break
            if temp:
                print(temp)
                self.executor.kafka_arrangement = temp
                if self.executor.kafka_arrangement["partition"] != "":
                    self.assign([TopicPartition(self.topic, self.executor.kafka_arrangement["partition"], self.executor.kafka_arrangement["offset_range"][0])])

            if not self.executor.kafka_arrangement or not self.executor.kafka_arrangement or self.executor.kafka_arrangement["partition"] == "":
                time.sleep(5)
                continue
            if self.executor.kafka_arrangement["offset_range"][0] <= self.executor.kafka_arrangement["offset_range"][1]:
                self.assign([TopicPartition(self.topic, self.executor.kafka_arrangement["partition"], self.executor.kafka_arrangement["offset_range"][0])])
            else:
                self.executor.kafka_arrangement = {}
                continue
            self.executor.kafka_arrangement["offset_range"][0] += 1

            logger.debug(self.assignment())
            return super().poll()
