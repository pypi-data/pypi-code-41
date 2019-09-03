from arps.core.agent import _AgentImplementation
from arps.core.environment import Environment
from arps.core.communication_layer import CommunicationLayer

from arps.core.policies.info import InfoProviderPolicy
from arps.core.policies.touchpoint_status import TouchPointStatusProviderPolicy
from arps.core.policies.meta import MetaPolicyProvider
from arps.core.policies.monitor import MonitorPolicy
from arps.core.policies.meta_agent import MetaAgentProviderPolicy
from arps.core.process_with_policies import build_process

from arps.core.remove_logger_files import remove_logger_files


class AgentCreationError(Exception):
    '''Error raised when agent creation fails

    '''


class AgentFactory:

    def __init__(self, *, metrics_loggers,
                 communication_layer: CommunicationLayer,
                 environment=None):
        '''Creates a new agent factory

        Keyword parameters:

        - metrics_logger: log activities such as number of messages
          exchanged, policies executed, etc.

        - communication_layer : specialization of communication_layer
          class

        - environment : Environment instance with sensors/actuators
        '''

        self._metrics_loggers = metrics_loggers

        assert communication_layer, 'Expect an instance of communication layer'
        self._communication_layer = communication_layer
        self._environment = environment or Environment()

    def create_agent(self, *, identifier, process):
        '''
        This function creates an agent

        Keyword parameters:
        - identifier: unique id
        - process: process instance
        '''

        sensors = [self._environment.sensor(
            sensor_id) for sensor_id in process.required_sensors()]
        actuators = [self._environment.actuator(
            actuator_id) for actuator_id in process.required_actuators()]

        metrics_logger = self._metrics_loggers.register(identifier)

        try:
            agent = _AgentImplementation(
                identifier=identifier,
                communication_layer=self._communication_layer,
                sensors=sensors,
                actuators=actuators,
                environment=self._environment,
                metrics_logger=metrics_logger)
            agent._add_process(process)
        except RuntimeError as error:
            raise AgentCreationError(str(error))

        return agent


def build_agent(agent_factory, policy_loader, agent_id, policies, period, clock):
    '''
    Build an agent according to its factory.

    Agent will have as default policy: InfoProviderPolicy, TouchPointStatusProviderPolicy,
                                       MetaPolicyProvider, MetaAgentProviderPolicy

    Raises AgentCreationError if preconditions for creation is not fulfilled
    '''
    try:
        user_policies = [policy_loader(policy) for policy in sorted(policies)]
    except KeyError as error:
        raise AgentCreationError(f'policy {error.args[0]} not registered for agent {agent_id}')

    default_policies = [
        InfoProviderPolicy(),
        TouchPointStatusProviderPolicy(),
        MetaPolicyProvider(),
        MetaAgentProviderPolicy()]

    policies = default_policies + user_policies

    monitor_policies = [p for p in policies if isinstance(p, MonitorPolicy)]
    if monitor_policies and not period:
        for monitor_policy in monitor_policies:
            remove_logger_files(monitor_policy.monitor_logger)

        raise AgentCreationError('Tried to create a monitor agent but no period is provided')

    process = build_process(policies, clock, period, str(agent_id))

    agent = agent_factory.create_agent(identifier=agent_id, process=process)

    for user_policy in user_policies:
        try:
            for required_metric in user_policy.required_metrics:
                agent.metrics_logger.add(required_metric)
        except AttributeError:  # for required_metrics
            pass

    return agent
