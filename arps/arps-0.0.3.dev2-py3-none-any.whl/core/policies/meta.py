from typing import Tuple

from arps.core.agent_id_manager import AgentID
from arps.core.environment import is_policy_registered
from arps.core.payload_factory import (PayloadType,
                                       Request,
                                       create_policy_response,
                                       MetaOp)
from arps.core.policy import ActionType, ReflexPolicy


class MetaPolicyProvider(ReflexPolicy):
    '''Provides a way to add, remove other policies

    To add or remove a policy, create a request using
    PayloadFactory.create_policy_request(...)

    If the policy exists, it will perform the operation trhough
    ActionType.event. Otherwise it will return an ActionType.result
    containing:

    - unknown operation, when 'op' content is unknown
    - unknown policy, when PolicyName contains an unregistered policy'

    See tests for more examples.

    '''

    def _condition(self, host, event, epoch) -> bool:
        '''
        Returns True if contains a request of PayloadType.policy
        '''
        if not isinstance(event, Request):
            self.logger.debug('Not a request, condition not met')
            return False

        is_policy = event.type == PayloadType.policy
        self.logger.debug(f'Event is a policy change request: {is_policy}')
        return is_policy

    def _action(self, host, event, epoch) -> Tuple[ActionType, bool]:
        '''
        Modifies an agent's policies by adding or removing the specified policy
        '''

        content = event.content

        sender_id = event.sender_id
        receiver_id = event.receiver_id
        message_id = event.message_id

        policy_name = content.meta
        if not is_policy_registered(host.identifier.root_id, policy_name):
            content = 'policy {} not registered'.format(policy_name)
            self.logger.debug(content)
            action = host.send(create_policy_response(receiver_id,
                                                      sender_id,
                                                      content,
                                                      message_id),
                               AgentID.from_str(sender_id))
            return (ActionType.event, action)

        action = None
        operation = content.op

        async def execute(op_function):
            op_function(policy_name)
            content = 'operation code {} about policy {} executed successfully'.format(
                operation, policy_name)
            await host.send(create_policy_response(receiver_id,
                                                   sender_id,
                                                   content,
                                                   message_id),
                            AgentID.from_str(sender_id))

        if operation == MetaOp.add:
            self.logger.info('add policy {} requested'.format(policy_name))
            action = execute(host.process.add_policy)
        elif operation == MetaOp.remove:
            self.logger.info('remove policy {} requested'.format(policy_name))
            action = execute(host.process.remove_policy)
        else:
            content = 'unknown operation code {}'.format(operation)
            self.logger.warning(content)
            action = host.send(create_policy_response(receiver_id,
                                                      sender_id,
                                                      content,
                                                      message_id),
                               AgentID.from_str(sender_id))

        return (ActionType.event, action)
