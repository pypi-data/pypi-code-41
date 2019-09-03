'''
This module contains a set of policies to use as dummy policies

DummyPolicy will always be True when a request event arrives and do nothing

DummyPolicyWithBehavior evaluate the condition using Sensors and modify Actuators when it is True

Sender and Receiver Policies are to implement a simple communication between agent.
Sender sends and Receiver increments number of messages received.
'''

import logging
from typing import Tuple

from arps.core.agent_id_manager import AgentID
from arps.core.payload_factory import (PayloadType,
                                       Request,
                                       create_action_request,
                                       create_action_response)
from arps.core.policy import ReflexPolicy
from arps.core.policy import ActionType
from arps.core.metrics_logger import PolicyEvaluatedMetric


class DummyPolicy(ReflexPolicy):
    '''
    Dummy policy for tests.
    '''

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__(
            required_sensors=[
                'SensorA', 'SensorB'], required_actuators=[
                'ActuatorA', 'ActuatorB'])

    def _condition(self, host, event, epoch) -> bool:
        '''
        Condition to be evaluated True when a event of type request is received
        '''
        condition = isinstance(event, Request)
        self.logger.info(f'Event is a request? {condition}')
        return condition

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        '''
        Returns the request in kwargs
        '''
        self.logger.info('result: {}'.format(event))
        return (ActionType.result, event)

    def __repr__(self):
        return 'DummyPolicy()'


class DummyPolicyWithBehavior(ReflexPolicy):
    '''
    Dummy policy for tests.
    '''

    def __init__(self, condition=None, action=None):
        self.logger = logging.getLogger(DummyPolicyWithBehavior.__name__)
        self.condition = condition or (lambda sensor_value: sensor_value > 10)
        self.action = action or (lambda: 1)
        super().__init__(required_sensors=['SensorB'], required_actuators=['ActuatorA'])

    def _condition(self, host, event, epoch) -> bool:
        '''
        Returns True if Sensor B value met condition defined by self.condition
        '''
        if not isinstance(event, Request):
            self.logger.info('Not a dummy policy with behaviour')
            return False

        periodic_payload = event.type == PayloadType.periodic_action
        sensor_value = host.read_sensor('SensorB')
        sensor_value = sensor_value if isinstance(sensor_value, int) else len(sensor_value)
        condition = periodic_payload and self.condition(sensor_value)

        self.logger.info(f'Condition {self.condition} met? {condition}')
        return condition


    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        '''
        Changes Actuator A to self.action returned value if condition is met
        '''
        current_state = host.read_actuator('ActuatorA')
        self.logger.info(f'current state of Actuator A: {current_state}')

        try:
            self.logger.info(f'Action {self.action}')
            host.modify_actuator('ActuatorA', value=current_state+self.action(),
                                 identifier=host.identifier, epoch=epoch)
        except ValueError as err:
            self.logger.warning(err)

        current_state = host.read_actuator('ActuatorA')
        self.logger.info('new state of Actuator A: {}'.format(current_state))

        return (ActionType.result, True)

    def __repr__(self):
        return 'Dummy Policy With Behavior'


class DummyPolicyForSimulator(DummyPolicyWithBehavior):

    def __init__(self):
        super().__init__(condition=DummyPolicyForSimulator._greater_than_40,
                         action=DummyPolicyForSimulator._decrement_resource_value)

    @staticmethod
    def _greater_than_40(sensor_value):
        return sensor_value >= 40

    @staticmethod
    def _decrement_resource_value():
        return -1


class DefaultDummyPolicyForSimulator(DummyPolicyWithBehavior):

    def __init__(self):
        super().__init__(condition=DefaultDummyPolicyForSimulator._less_than_40,
                         action=DefaultDummyPolicyForSimulator._increment_resource_value)

    @staticmethod
    def _less_than_40(sensor_value):
        return sensor_value < 40

    @staticmethod
    def _increment_resource_value():
        return 1


class SenderPolicy(ReflexPolicy):
    required_metrics = [PolicyEvaluatedMetric]

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(SenderPolicy.__name__)
        super().__init__(*args, **kwargs)

    def _condition(self, host, event, epoch) -> bool:
        if not isinstance(event, Request):
            self.logger.info('Event is not a periodic action request')
            return False

        a_periodic_action = event.type == PayloadType.periodic_action
        self.logger.info(f'Event is a periodic action request: {a_periodic_action}')
        return a_periodic_action

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        sender_id = event.receiver_id

        async def dummy_event():
            for related_agent in host.related_agents:
                self.logger.info('Sending action to %s', str(related_agent))
                message = create_action_request(sender_id, str(related_agent),
                                                None, event.message_id)
                await host.send(message, related_agent)
                self.logger.info('Event to %s created', related_agent)

        host.metrics_logger.update_policies_evaluated(SenderPolicy.__name__, epoch)
        return (ActionType.event, dummy_event())


class ReceiverPolicy(ReflexPolicy):
    required_metrics = [PolicyEvaluatedMetric]

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(ReceiverPolicy.__name__)
        super().__init__(required_sensors=[], required_actuators=['ActuatorA'], *args, **kwargs)

    def _condition(self, host, event, epoch) -> bool:
        if not isinstance(event, Request):
            self.logger.info('Event is not an action request')
            return False

        an_action = event.type == PayloadType.action
        self.logger.info(f'Event is an action request: {an_action}')
        return an_action

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        value = host.read_actuator('ActuatorA')
        host.modify_actuator('ActuatorA',
                             value=value+1,
                             epoch=epoch,
                             identifier=host.identifier)
        self.logger.info('Actuator modified to %s', host.read_actuator('ActuatorA'))
        host.metrics_logger.update_policies_evaluated(ReceiverPolicy.__name__, epoch)

        sender_id = event.receiver_id
        receiver_id = event.sender_id
        content = f'Executed action requested by {receiver_id}'
        message = create_action_response(sender_id, receiver_id,
                                         content, event.message_id)

        return (ActionType.event, host.send(message, AgentID.from_str(receiver_id)))
