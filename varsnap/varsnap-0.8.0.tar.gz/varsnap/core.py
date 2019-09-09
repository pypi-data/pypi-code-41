import base64
try:
    from collections.abc import Iterable, Mapping
except ImportError:  # Python 2 compatibility
    from collections import Iterable, Mapping
import json
try:
    from json.decode import JSONDecodeError
except ImportError:  # Python 2 compatibility
    JSONDecodeError = ValueError
import logging
import os
import pickle
import six
import sys
import threading
import time
import traceback

from qualname import qualname
import requests

from .__version__ import __version__

PRODUCE_SNAP_URL = 'https://www.varsnap.com/api/snap/produce/'
CONSUME_SNAP_URL = 'https://www.varsnap.com/api/snap/consume/'
PRODUCE_TRIAL_URL = 'https://www.varsnap.com/api/trial/produce/'

# Names of different environment variables used by varsnap
# See readme for descriptions
ENV_VARSNAP = 'VARSNAP'
ENV_ENV = 'ENV'
ENV_PRODUCER_TOKEN = 'VARSNAP_PRODUCER_TOKEN'
ENV_CONSUMER_TOKEN = 'VARSNAP_CONSUMER_TOKEN'

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(handler)

# A list of VarSnap functions for testing and tracing
CONSUMERS = []
PRODUCERS = []


def env_var(env):
    return os.environ.get(env, '').lower()


def get_signature(target_func):
    return 'python.%s.%s' % (__version__, qualname(target_func))


def equal(x, y):
    if not isinstance(x, y.__class__):
        return False
    if isinstance(x, six.string_types):
        return x == y
    if isinstance(x, Iterable):
        if len(x) != len(y):
            return False
        mapping = isinstance(x, Mapping)
        for v in zip(x, y):
            if not equal(v[0], v[1]):
                return False
            if mapping and not equal(x[v[0]], y[v[1]]):
                return False
        return True
    if hasattr(x, '__dict__'):
        return equal(x.__dict__, y.__dict__)
    return x == y


class Producer():
    def __init__(self, target_func):
        self.target_func = target_func
        PRODUCERS.append(self)

    @staticmethod
    def is_enabled():
        if env_var(ENV_VARSNAP) != 'true':
            return False
        if env_var(ENV_ENV) != 'production':
            return False
        if not env_var(ENV_PRODUCER_TOKEN):
            return False
        return True

    @staticmethod
    def serialize(data):
        data = base64.b64encode(pickle.dumps(data)).decode('utf-8')
        return data

    @staticmethod
    def get_globals():
        global_vars = {}
        for k, v in globals().items():
            if k[:2] == '__':
                continue
            try:
                pickle.dumps(v)
            # Ignore unpickable data
            except (TypeError, AttributeError, pickle.PicklingError):
                continue
            global_vars[k] = v
        return global_vars

    def produce(self, args, kwargs, output):
        if not Producer.is_enabled():
            return
        LOGGER.info(
            'VarSnap producing call for %s' %
            qualname(self.target_func)
        )
        global_vars = Producer.get_globals()
        data = {
            'producer_token': env_var(ENV_PRODUCER_TOKEN),
            'signature': get_signature(self.target_func),
            'inputs': Producer.serialize([args, kwargs, global_vars]),
            'prod_outputs': Producer.serialize(output)
        }
        requests.post(PRODUCE_SNAP_URL, data=data)


class Consumer():
    def __init__(self, target_func):
        self.target_func = target_func
        self.last_snap_id = None
        CONSUMERS.append(self)

    @staticmethod
    def is_enabled():
        if env_var(ENV_VARSNAP) != 'true':
            return False
        if env_var(ENV_ENV) != 'development':
            return False
        if not env_var(ENV_CONSUMER_TOKEN):
            return False
        return True

    @staticmethod
    def deserialize(data):
        try:
            data = pickle.loads(base64.b64decode(data.encode('utf-8')))
        except ImportError as e:
            raise pickle.UnpicklingError(e)
        return data

    def consume_watch(self):
        if not Consumer.is_enabled():
            return
        LOGGER.info(
            'VarSnap consuming calls to %s' %
            qualname(self.target_func)
        )
        while True:
            self.consume()
            time.sleep(1)

    def consume(self):
        data = {
            'consumer_token': env_var(ENV_CONSUMER_TOKEN),
            'signature': get_signature(self.target_func),
        }
        response = requests.post(CONSUME_SNAP_URL, data=data)
        try:
            response_data = json.loads(response.content)
        except JSONDecodeError:
            response_data = ''
        if (not response_data or
                response_data['status'] != 'ok' or
                len(response_data['results']) == 0):
            return
        snap_data = response_data['results'][0]
        if snap_data['id'] == self.last_snap_id:
            return

        self.last_snap_id = snap_data['id']
        LOGGER.info(
            'Receiving call from Varsnap uuid: ' + str(self.last_snap_id)
        )
        try:
            inputs = Consumer.deserialize(snap_data['inputs'])
            prod_outputs = Consumer.deserialize(snap_data['prod_outputs'])
        except pickle.UnpicklingError:
            return
        exception = ''
        for k, v in inputs[2].items():
            globals()[k] = v
        try:
            local_outputs = self.target_func(*inputs[0], **inputs[1])
        except Exception as e:
            local_outputs = e
            exception = traceback.format_exc()
        if exception:
            matches = equal(prod_outputs, exception)
        else:
            matches = equal(prod_outputs, local_outputs)
        self.report_central(
            data['consumer_token'], snap_data['id'], local_outputs, matches
        )
        log = self.report_log(
            inputs, prod_outputs, local_outputs, exception, matches
        )
        return matches, log

    def report_central(self, consumer_token, snap_id, local_outputs, matches):
        data = {
            'consumer_token': consumer_token,
            'snap_id': snap_id,
            'dev_outputs': local_outputs,
            'matches': matches,
        }
        requests.post(PRODUCE_TRIAL_URL, data=data)

    def report_log(
        self, inputs, prod_outputs, local_outputs, exception, matches
    ):
        function_name = qualname(self.target_func)
        report = []
        report.append(('Function:', function_name))
        report.append(('Function input args:', inputs[0]))
        report.append(('Function input kwargs:', inputs[1]))
        report.append(('Production function outputs:', prod_outputs))
        report.append(('Your function outputs:', local_outputs))
        if exception:
            report.append(('Local exception:', exception))
        report.append(('Matching outputs:', matches))

        # Vertically align report's second column
        key_length = max([len(x[0]) for x in report]) + 2
        report = [(x[0] + ' '*(key_length - len(x[0])), x[1]) for x in report]
        report = [x[0] + str(x[1]) for x in report]
        log = "\n".join(report)

        if matches:
            LOGGER.info(log)
        else:
            LOGGER.error(log)
        return log


def varsnap(func):
    producer = Producer(func)
    Consumer(func)

    def magic(*args, **kwargs):
        try:
            output = func(*args, **kwargs)
        except Exception as e:
            threading.Thread(
                target=producer.produce,
                args=(args, kwargs, e),
            ).start()
            raise
        threading.Thread(
            target=producer.produce,
            args=(args, kwargs, output),
        ).start()
        return output
    LOGGER.info('Varsnap Loaded')
    # Reuse the original function name so it works with flask handlers
    magic.__name__ = func.__name__
    return magic
