import contextlib
import asyncio

import pytest

from arps.core.environment import register_policy
from arps.core.environment import unregister_policy

from arps.core.real.rest_api_utils import random_port

from arps.core.clock import simulator_clock_factory

from arps.core.real.raw_communication_layer import RawCommunicationLayer
from arps.core.real.rest_communication_layer import RESTCommunicationLayer

from arps.test_resources.fake_agents_directory_helper import FakeAgentsDirectoryHelper
from arps.core.remove_logger_files import remove_logger_files

from arps.apps.agent_runner import AgentHandler


@contextlib.contextmanager
def setup_agent_handler(policies,
                        environment,
                        clock,
                        agent_id,
                        agents_directory_helper,
                        comm_layer_cls,
                        trigger_event_period=0):
    # Specification of any policies that has touchpoints are required in this tests,
    # since the agent per se does nothing, only provides the interfaces to get info,
    # touchpoint status, and change its policy
    agent_port = random_port()

    policies = policies or []

    for policy in policies:
        register_policy(agent_id.agent_identifier, policy.__name__, policy)

    policies_by_name = [policy.__name__ for policy in policies]

    try:
        agent_handler = AgentHandler(environment=environment,
                                     clock=clock,
                                     agent_id=agent_id,
                                     agent_port=agent_port,
                                     agents_directory_helper=agents_directory_helper,
                                     trigger_event_period=trigger_event_period,
                                     policies=policies_by_name,
                                     comm_layer_cls=comm_layer_cls)
        yield agent_handler

        remove_logger_files(agent_handler.agent.metrics_logger.logger)
    finally:
        for policy in policies:
            unregister_policy(agent_id.agent_identifier, policy.__name__)


@pytest.fixture(params=(RawCommunicationLayer, RESTCommunicationLayer))
async def real_env_components(request):
    agents_directory_helper = FakeAgentsDirectoryHelper()
    clock = simulator_clock_factory()

    clock_task = asyncio.create_task(clock.run())

    yield clock, agents_directory_helper, request.param

    clock_task.cancel()
