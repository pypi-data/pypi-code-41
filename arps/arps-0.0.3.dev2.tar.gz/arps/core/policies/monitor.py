'''This module contain a base class that enable agents to monitor a
specific resource

The resource state is saved in disk and it is expected to retrieved
using the way the state is persisted

This is related to metrics_logger module in a way that both are made
to collect data

'''
import logging
from functools import reduce
from io import StringIO
from collections import defaultdict
from typing import List, Tuple

import pandas as pd

from arps.core.payload_factory import (PayloadType,
                                       Request,
                                       Response,
                                       create_action_response)
from arps.core.policy import ReflexPolicy, ActionType
from arps.core.agent_id_manager import AgentID
from arps.core import logger_setup


class MonitorPolicy(ReflexPolicy):
    '''
    This class will periodically gather the resource state
    '''

    def __init__(self, *, required_sensors, required_actuators):
        '''Initialize with required sensors and required_actuators

        These touchpoints are going to be read and their state will be
        stored for later usage by other agents/human beings

        The touchpoints are saved on a file named monitor_[TOUCHPOINT]_timestamp.log

        '''
        super().__init__(required_sensors, required_actuators)

        touchpoint = self.required_sensors() or self.required_actuators()
        self.monitor_logger = self._build_monitor_logger(touchpoint[0])

    def _build_monitor_logger(self, required_touchpoint):
        '''
        Build each monitor logger
        '''
        logger = logging.getLogger(required_touchpoint)
        logger_setup.set_to_rotate(logger, f'monitor_{required_touchpoint}',
                                   header_field=required_touchpoint)
        return logger

    def _condition(self, host, event, epoch) -> bool:
        if not isinstance(event, Request):
            self.logger.debug('Not an action or a periodic action to request')
            return False

        is_action = event.type in (PayloadType.periodic_action,
                                   PayloadType.action)
        self.logger.debug(f'Event is an action or a periodic action request: {is_action}')
        return is_action

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        if event.type == PayloadType.periodic_action:
            return self.log_touchpoint(host)

        if event.type == PayloadType.action:
            return self.create_action_response(host, event)

        raise RuntimeError(f"It is not supposed to reach this state. Payload type {event['request']['type']}")

    def log_touchpoint(self, host):
        sensors = self.required_sensors()
        if sensors:
            sensor_state = host.read_sensor(sensors[0])
            self.monitor_logger.info(sensor_state)

        actuators = self.required_actuators()
        if actuators:
            actuator_state = host.read_actuator(actuators[0])
            self.monitor_logger.info(actuator_state)

        return (ActionType.result, True)

    def create_action_response(self, host, request):
        sender_id = request.sender_id
        receiver_id = request.receiver_id
        message_id = request.message_id
        logger_file_name_prefix = self.monitor_logger.handlers[0].baseFilename
        message = create_action_response(receiver_id, sender_id,
                                         logger_file_name_prefix, message_id)
        return (ActionType.event, host.send(message,
                                            AgentID.from_str(sender_id)))


def build_monitor_policy_class(name, sensor=None, actuator=None):
    if sensor and actuator:
        raise RuntimeError('Expecting only a sensor or an actuator. Cannot be both')

    required_sensors = [sensor] if sensor else []
    required_actuators = [actuator] if actuator else []

    def monitor_policy_init(self):
        super(self.__class__, self).__init__(required_sensors=required_sensors,
                                             required_actuators=required_actuators)

    return type(name, (MonitorPolicy,), {'__init__': monitor_policy_init})


class MonitorResponsePolicy(ReflexPolicy):

    def _condition(self, host, event, epoch) -> bool:
        if not isinstance(event, Response):
            self.logger('Not a monitor response response')
            return False

        is_action = event.type == PayloadType.action
        self.logger.debug(f'Event is an action or a periodic action response: {is_action}')
        return is_action

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        return (ActionType.result, event)


def merge_monitor_logs(logs: List[str]) -> str:
    '''
    Merge multiple logs from monitors into a single log. Each monitor will have its own column in a CSV file

    Args:
    - logs: list of path to the logs
    '''

    logs_as_csv = [pd.read_csv(log, sep=';').drop('level', axis=1) for log in logs]

    #Add a new column to make it easier to merge columns based on time
    add_count_time_into_logs(logs_as_csv)

    result = reduce(lambda left, right: pd.merge(left, right, how='outer', on=['date', 'time', 'count_time']), logs_as_csv)
    result.drop('count_time', axis=1, inplace=True)
    result.sort_values(axis=0, by=['date', 'time'], inplace=True)

    csv_buffer = StringIO()
    result.to_csv(csv_buffer, index=False)

    return csv_buffer.getvalue()


def add_count_time_into_logs(logs_as_csv):
    for log in logs_as_csv:
        log['count_time'] = fastcount(log.time.values)


def fastcount(x):
    '''Count occurences in the log. This was done to make it able to
    merge files with repeated values

    '''
    def cg(x):
        cnt = defaultdict(lambda: 0)

        for j in x.tolist():
            cnt[j] += 1
            yield cnt[j]

    return [i for i in cg(x)]
