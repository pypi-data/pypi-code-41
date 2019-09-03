import asyncio
from functools import partial, update_wrapper
import logging
from typing import List, Any

from arps.core.clock import Clock
from arps.core.environment import load_policy
from arps.core.policy import ActionType
from arps.core.payload_factory import (Payload,
                                       create_periodic_action)


class ProcessWithPolicies:

    def __init__(self, policies=None, epoch_time=None):
        '''
        Initializes process that deal with policies

        Keyword Args:
        - policies: list of policies that will be used to evaluate received events
        - epoch_time: epoch time to provide info when an event was processed
        '''
        self._policies = policies or list()
        self._epoch_time = epoch_time
        self._events_received: List[Payload] = list()
        self.policy_action_results = list()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = None

    def receive(self, event: Payload):
        '''
        Receive event to be added into the event loop

        Keyword parameters:
        - event : event received in PayloadFactory message format

        '''
        self.logger.info('event received %s by agent %s', event, self.host.identifier)
        assert self.host

        self._events_received.append(event)

    def add_policy(self, policy_identifier):
        '''
        Append policy into current policies

        Keyword parameters:
        - policy_identifier: policy's name
        '''
        policy = load_policy(self.host.identifier.root_id, policy_identifier)
        if self.host:
            self.host.update_touchpoints(
                policy.required_sensors(),
                policy.required_actuators())
        self._policies.append(policy)

    def remove_policy(self, policy_identifier):
        '''
        Removes policy from current policies

        Keyword parameters:
        - policy_identifier: policy's name
        '''

        instance = {
            policy.__class__.__name__: policy for policy in self._policies}
        self._policies.remove(instance[policy_identifier])

    @property
    def policies_name(self):
        return [policy.__class__.__name__ for policy in self._policies]

    def required_sensors(self):
        '''
        Returns required sensors according to the current policies
        '''
        sensors = [policy.required_sensors() for policy in self._policies]
        return sum(sensors, [])

    def required_actuators(self):
        '''
        Returns required actuators according to the current policies
        '''
        actuators = [policy.required_actuators() for policy in self._policies]
        return sum(actuators, [])

    async def run(self):
        '''event to be called by event loop

        Depending on the type of event:
        - an action can be executed
        - a result can be stored to be retrieve later accessing
          policy_action_results
        '''
        policies_result = self._policies_result()
        await self._process_results(policies_result)

    def _policies_result(self):
        '''
        Collect events received and run against current policies

        Returns policies result
        '''
        policies_result = list()

        self.logger.debug(f'checking for events received: {len(self._events_received)}')
        while self._events_received:
            event_received = self._events_received.pop()
            self.logger.debug('Running event %s on: %s', event_received, self._policies)
            policies_result.extend([
                policy.event(
                    event=event_received,
                    host=self.host,
                    epoch=self._epoch_time.epoch) for policy in self._policies])

        return [result for result in policies_result if result]

    async def _process_results(self, policies_result):
        '''
        Process results according to their types

        Event will be execute while an event will be stored
        '''

        while policies_result:
            (action_type, content) = policies_result.pop()
            self.logger.debug('action type to process: {}'.format(action_type.name))

            if action_type == ActionType.event:
                try:
                    self.logger.debug('Content {}'.format(content))
                    if asyncio.iscoroutinefunction(content):
                        await content()
                    elif asyncio.iscoroutine(content):
                        await content
                    else:
                        content()
                    self.logger.debug('action type event executed')
                except Exception as e:
                    self.logger.error('Exception: {}'.format(e))
                    raise e
                except:
                    raise RuntimeError('something not expected happened')
                    self.logger.error('something not expected happened')

            if action_type == ActionType.result:
                self.policy_action_results.append(content)

    def __repr__(self):
        return repr([policy for policy in self._policies])

class ProcessWithEvents(ProcessWithPolicies):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.periodic_events = list()

    def _receive_periodic_events(self, periodic_event, time_event):
        self.logger.debug('Periodic event executed on {}'.format(time_event.value))
        self.periodic_events.append(periodic_event)

    async def run(self):
        for periodic_event in self.periodic_events:
            self.receive(periodic_event)
        self.periodic_events.clear()
        await super().run()


def build_process(policies: List[Any], clock: Clock, period: int, agent_id: str) -> ProcessWithPolicies:
    '''
    Build process based on its periodicity

    Args:
    - policies: List containing policies
    - clock: instance of Clock
    - period: epochs between one execution and the next one
    - agent_id: agent identifier
    '''

    if period is None or not period > 0:
        return ProcessWithPolicies(policies=policies, epoch_time=clock.epoch_time)

    process = ProcessWithEvents(policies=policies, epoch_time=clock.epoch_time)
    periodic_event = create_periodic_action(sender_id=agent_id, receiver_id=agent_id)
    receive_periodic_events = partial(process._receive_periodic_events, periodic_event)
    update_wrapper(receive_periodic_events, process._receive_periodic_events)
    clock.add_listener(receive_periodic_events,
                       lambda event: event.value % period == 0)

    return process
