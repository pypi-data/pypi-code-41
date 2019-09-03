import logging

from enum import IntEnum
from collections import abc
from typing import Tuple


class ActionType(IntEnum):
    event = 0,
    result = 1


class ReflexPolicy:
    '''
    Policy based on Event Condition Action
    '''

    def __init__(self, required_sensors=None, required_actuators=None):
        '''
        The __init__ method should be called by derived classes to
        defined required sensors and actuators

        Keyword parameters:
        - required_sensors : required sensors that will be read by policy
        - required_actuators : required actuators that will be controlled by policy
        '''

        self._required_sensors = required_sensors or []
        self._required_actuators = required_actuators or []
        is_sequence = lambda parameter: isinstance(parameter, abc.Sequence)
        if not (is_sequence(self._required_sensors) and is_sequence(self._required_actuators)):
            message = 'Expected a sequence for required sensors/actuators, got {}/{}'
            raise ValueError(message.format(type(self._required_sensors),
                                            type(self._required_actuators)))

        self.logger = logging.getLogger(self.__class__.__name__)

    def required_sensors(self):
        '''
        Return all required sensors that are necessary by a policy
        '''
        return self._required_sensors

    def required_actuators(self):
        '''
        Return all required actuators that are necessary by a policy
        '''
        return self._required_actuators

    def event(self, host, event, epoch):
        '''
        Method that will receive the event to be verified
        if the condition is met an action is performed

        Args:
        - host: the agent where the policy is hosted
        - event: event received by the agent
        - epoch: the moment when the event occurred

        Raise:
        - RuntimeError if action does not return a result
        '''

        self.logger.debug('event on host {}'.format(host.identifier))
        if self._condition(host, event, epoch):
            result = self._action(host, event, epoch)
            if not result:
                raise RuntimeError('action executed, but no result returned')

            return result

        return None

    def _condition(self, host, event, epoch) -> bool:
        '''
        Condition to be evaluated when a event is received

        Args:
        - host: the agent where the policy is hosted
        - event: event received by the agent
        - epoch: the moment when the event occurred
        '''
        return True

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        '''
        Returns a tuple containing ActionType and the event or result

        Args:
        - host: the agent where the policy is hosted
        - event: event received by the agent
        - epoch: the moment when the event occurred
        '''
        return (ActionType.result, True)

    def __repr__(self):
        return f'{self.__class__.__name__}()'
