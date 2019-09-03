from __future__ import annotations
from enum import IntEnum, unique
from typing import Union, Any, Dict, List
from dataclasses import dataclass, field


@unique
class PayloadType(IntEnum):
    '''Payload type to classify messages

    Payloads that will have a request and response

        * info - related to request/response info about the agent
        * sensors - related to request/response sensors values about
          the agent
        * actuators - related to request/response actuators values
          about the agent
        * policy - related to request/response on changing agents
          policies
        * meta_agent - related to request/response on changing agents
          related to other agents

    Payloads that will have an action to be executed

        * periodic_action - related to messages that execute periodically
        * action - related to messages that execute only once. The
          payload can be anything.

    Control related type:

       * error - contains a message describing an error that occurred
    after receiving a request

    '''
    info = 0
    sensors = 1
    actuators = 2
    policy = 3
    meta_agent = 4
    periodic_action = 5
    action = 6
    error = 7


@dataclass
class BasePayload:
    sender_id: str
    receiver_id: str
    type: PayloadType
    message_id: Any = field(default=None)
    content: Any = field(default=None)


class Request(BasePayload):
    '''Payload of Request Type
    '''


class Response(BasePayload):
    '''Payload of Response Type
    '''


@dataclass
class Info:
    sensors: List[str]
    actuators: List[str]
    policies: List[str]
    related_agents: List[str]


@dataclass
class TouchPoint:
    touchpoint: Dict[str, Union[str, int]]


@dataclass
class Meta:
    '''This class has the purpose of describing a operation (MetaOP) that
    will take place in the agent. The MetaOP to be executed is described
    in the meta field

    '''
    op: MetaOp
    meta: Any


class MetaOp(IntEnum):
    add = 0
    remove = 1


@dataclass
class Status:
    status: str


@dataclass
class Action:
    action: str


Payload = Union[Request, Response]


def create_info_request(sender_id, receiver_id, message_id):
    return Request(sender_id,
                   receiver_id,
                   PayloadType.info,
                   message_id)


def create_info_response(sender_id, receiver_id, sensors, actuators,
                         policies, related_agents, message_id):
    return Response(sender_id,
                    receiver_id,
                    PayloadType.info,
                    message_id,
                    Info(sensors,
                         actuators,
                         policies,
                         related_agents))


def create_touchpoint_request(sender_id, receiver_id, touchpoint_type,
                              message_id):
    assert touchpoint_type in (PayloadType.sensors,
                               PayloadType.actuators)
    return Request(sender_id,
                   receiver_id,
                   touchpoint_type,
                   message_id)


def create_touchpoint_response(sender_id, receiver_id, touchpoint_type,
                               touchpoint, message_id):
    assert touchpoint_type in (PayloadType.sensors,
                               PayloadType.actuators)
    assert isinstance(touchpoint, dict)
    return Response(sender_id,
                    receiver_id,
                    touchpoint_type,
                    message_id,
                    TouchPoint(touchpoint))


def create_policy_request(sender_id, receiver_id, operation,
                          policy_name, message_id):
    return create_meta_request(sender_id, receiver_id, PayloadType.policy,
                               operation, policy_name, message_id)


def create_policy_response(sender_id, receiver_id,
                           response_content, message_id):
    return create_meta_response(sender_id, receiver_id, PayloadType.policy,
                                response_content, message_id)


def create_meta_agent_request(sender_id, receiver_id, operation,
                              agents_id, message_id):
    return create_meta_request(sender_id, receiver_id, PayloadType.meta_agent,
                               operation, agents_id, message_id)


def create_meta_agent_response(sender_id, receiver_id,
                               response_content, message_id):
    return create_meta_response(sender_id, receiver_id, PayloadType.meta_agent,
                                response_content, message_id)


def create_meta_request(sender_id, receiver_id, meta_type,
                        operation, parameters, message_id):
    assert meta_type in (PayloadType.meta_agent, PayloadType.policy)
    return Request(sender_id,
                   receiver_id,
                   meta_type,
                   message_id,
                   Meta(operation, parameters))


def create_meta_response(sender_id, receiver_id, meta_type,
                         response_content, message_id):
    assert meta_type in (PayloadType.meta_agent, PayloadType.policy)
    return Response(sender_id,
                    receiver_id,
                    meta_type,
                    message_id,
                    Status(response_content))


def create_periodic_action(sender_id, receiver_id):
    return Request(sender_id,
                   receiver_id,
                   PayloadType.periodic_action)


def create_action_request(sender_id, receiver_id, action, message_id=None):
    '''message_id is optional because sometimes the agent does not
    respond, it just perform the requested action

    '''
    return Request(sender_id,
                   receiver_id,
                   PayloadType.action,
                   message_id,
                   Action(action))


def create_action_response(sender_id, receiver_id, action, message_id):
    return Response(sender_id,
                    receiver_id,
                    PayloadType.action,
                    message_id,
                    Status(action))


def create_error_response(sender_id, receiver_id, message_id, error_message):
    return Response(sender_id,
                    receiver_id,
                    PayloadType.error,
                    message_id,
                    error_message)


def request_factory(payload_type: PayloadType,
                    sender_id: str,
                    receiver_id: str,
                    message_id: Any,
                    content: Any = None):
    '''Create request payload accordingly to the payload_type argument

    Args:
    - payload_type: instance of PayloadType
    - sender_id: Sender's AgentID
    - receiver_id: Receiver's AgentID
    - message_id: message id
    - content: payload_type dependent argument

    '''
    if payload_type == PayloadType.info:
        return create_info_request(sender_id, receiver_id, message_id)
    elif payload_type in (PayloadType.sensors, PayloadType.actuators):
        return create_touchpoint_request(sender_id, receiver_id,
                                         payload_type, message_id)
    elif payload_type == PayloadType.policy and content:
        operation = content[0]
        policy_name = content[1]
        return create_policy_request(sender_id, receiver_id,
                                     MetaOp[operation], policy_name,
                                     message_id)
    elif payload_type == PayloadType.meta_agent and content:
        operation = content['operation']
        to_agent = content['to_agent']
        return create_meta_agent_request(sender_id, receiver_id,
                                         MetaOp[operation], to_agent, message_id)
    elif payload_type == PayloadType.action:
        return create_action_request(sender_id, receiver_id, content, message_id)
    else:
        raise ValueError('Unexpected payload type or missing required content')


def response_factory(payload_type: PayloadType,
                     sender_id: str,
                     receiver_id: str,
                     message_id: Any,
                     content: Any):
    '''Create response payload accordingly to the payload_type argument

    Args:
    - payload_type: instance of PayloadType
    - sender_id: Sender's AgentID in str format
    - receiver_id: Receiver's AgentID in str format
    - message_id: message id
      communication is asynchronouts
    - content: payload_type dependent argument

    '''
    if payload_type == PayloadType.info:
        sensors, actuators, policies, related_agents = content
        return create_info_response(sender_id, receiver_id, sensors, actuators,
                                    policies, related_agents, message_id)
    elif payload_type in (PayloadType.sensors,
                          PayloadType.actuators):
        return create_touchpoint_response(sender_id, receiver_id,
                                          payload_type, content, message_id)
    elif payload_type == PayloadType.policy:
        return create_policy_response(sender_id, receiver_id, content, message_id)
    elif payload_type == PayloadType.meta_agent:
        return create_meta_agent_response(sender_id, receiver_id, content, message_id)
    elif payload_type == PayloadType.action:
        return create_action_response(sender_id, receiver_id, content, message_id)
    elif payload_type == PayloadType.error:
        return create_error_response(sender_id, receiver_id, message_id, content)
    else:
        raise ValueError(f'Could not create response: unexpected payload type {payload_type}')


def parse_payload_type(payload_type: Union[int, str, PayloadType]):
    '''
    Arguments:
    - payload_type : PayloadType
    '''
    try:
        return PayloadType[payload_type]
    except KeyError:
        try:
            return PayloadType(payload_type)
        except ValueError:
            raise ValueError(f'Expect a type from PayloadType , received {type(payload_type)}')
