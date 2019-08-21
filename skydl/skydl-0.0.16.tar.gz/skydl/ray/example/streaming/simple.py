from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import time
import ray
from ray.experimental.streaming.communication import QueueConfig
from ray.experimental.streaming.streaming import Environment
from ray.experimental.streaming.batched_queue import BatchedQueue
from ray.experimental.streaming.operator import OpType, PStrategy
from py_common_util.common.date_utils import DateUtils

# define logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def splitter(line):
    # return line.split()
    return line + "-by-splitter"


def filter_fn(word):
    if "f" in word:
        return True
    return False


class CustormConfig(object):
    def __init__(self, parallelism=1):
        self.queue_config = QueueConfig(
            max_size=999999,
            max_batch_size=99999,
            max_batch_time=0.01,
            prefetch_depth=10,
            background_flush=False)
        self.parallelism = parallelism


if __name__ == "__main__":
    ray.init(redis_address="192.168.95.27:6379")
    ray.register_custom_serializer(BatchedQueue, use_pickle=True)
    ray.register_custom_serializer(OpType, use_pickle=True)
    ray.register_custom_serializer(PStrategy, use_pickle=True)
    env = Environment(CustormConfig())

    def attribute_selector(tuple):
        return tuple[1]

    def key_selector(tuple):
        return tuple[0]

    class CustormSource:
        def __init__(self):
            self._count = 0

        def get_next(self):
            self._count += 1
            if self._count % 20 == 0:
                # print("***get_next_nvl***:" + str(self._count))
                return str(self._count) + "-uuunited\nStates-" + DateUtils.now_to_str()
            else:
                return str(self._count) + "-United States-" + DateUtils.now_to_str()

    def print_log(content):
        logger.info(content)
        time.sleep(10)
        logger.info(content + ",finished:" + DateUtils.now_to_str())

    stream = env.source(CustormSource()) \
                .set_parallelism(10) \
                .inspect(print_log)\
                .set_parallelism(10)

    # stream = env.read_text_file(args.input_file) \
    #             .shuffle() \
    #             .flat_map(splitter) \
    #             .set_parallelism(2) \
    #             .key_by(key_selector) \
    #             .sum(attribute_selector) \
    #             .inspect(print)  # Prints the contents of the
    start = time.time()
    env_handle = env.execute()
    ray.get(env_handle)
    end = time.time()
    logger.info("Elapsed time: {} secs".format(end - start))
    logger.info("Output stream id: {}".format(stream.id))
    print("end!")
