import argparse
import sys
import logging
import signal
import platform
from functools import partial
import asyncio

from arps.core.agent_factory import (AgentFactory,
                                     AgentCreationError,
                                     build_agent)
from arps.core.agent_id_manager import AgentID
from arps.core.real.real_communication_layer import RealCommunicationLayer
from arps.core.real.raw_communication_layer import RawCommunicationLayer
from arps.core.real.rest_communication_layer import RESTCommunicationLayer
from arps.core.environment import load_policy
from arps.core.clock import real_time_clock_factory
from arps.core.metrics_logger import MetricsLoggers
from arps.core import logger_setup
from arps.core.remove_logger_files import remove_logger_files

from arps.apps.agents_directory_helper import AgentsDirectoryHelper
from arps.apps.configuration_file_loader import load_agent_environment
from arps.apps.pid import create_pid_file

# pylint: disable-msg=C0103


class AgentHandler:
    '''
    This class control the life cycle of an agent.

    By default the agent will be listening the port 8888

    Raises AgentCreationError from build_agent when agent creation fails.
    '''

    def __init__(self,
                 environment,
                 clock,
                 agent_id,
                 agent_port=8888,
                 policies=None,
                 trigger_event_period=0,
                 agents_directory_helper=None,
                 comm_layer_cls=None):
        '''Initialize agent handler instance

        Params:
        - environment: agent environment
        - agent_id: instance of AgentID created by AgentIDManager
        - agent_port: listening port (default: 8888)
        - policies: policies that will control the agent behaviour
        - trigger_event_period: granularity on how often agent should
          apply policies (required for MonitorPolicies)
        - agents_directory_helper: agents discovery service where the
          agent will be registered
        - comm_layer_cls: implementation of RealCommunicationLayer
        '''
        assert issubclass(comm_layer_cls, RealCommunicationLayer)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.agent_id = agent_id
        self.communication_layer = comm_layer_cls(agent_port,
                                                  agents_directory_helper)

        self.clock = clock
        try:
            agent_factory = AgentFactory(environment=environment,
                                         communication_layer=self.communication_layer,
                                         metrics_loggers=MetricsLoggers())
            self.agent = self.create_agent(agent_factory,
                                           agent_id=self.agent_id,
                                           policies=policies or [], clock=clock,
                                           trigger_event_period=trigger_event_period)
        except AgentCreationError as err:
            self.logger.error(err)
            raise RuntimeError(err)
        self.port = agent_port
        self.logger.info(f'created agent server {self.agent_id} to listen on {agent_port}')

    async def start(self):
        self.logger.info('agent has started')
        await self.communication_layer.start()
        self.clock.add_listener(self.agent.run)

    async def finalize(self):
        self.communication_layer.unregister(self.agent.identifier)
        await self.communication_layer.close()
        self.logger.info('agent has stopped')

    def create_agent(self, agent_factory,
                     agent_id, policies,
                     clock,
                     trigger_event_period):
        policy_loader = partial(load_policy, agent_id.agent_identifier)
        self.logger.info('Policies: {}'.format(policies))
        agent = build_agent(agent_factory,
                            policy_loader,
                            agent_id,
                            policies,
                            trigger_event_period,
                            clock)

        return agent


def main():
    # with open('agent_runner.log', 'a') as f:
    #     f.write(str(os.getpid()) + '\n')

    parser = build_argument_parser()

    parsed_args = parser.parse_args(sys.argv[1:])

    if platform.system() == 'Windows':
        def interrupt_application(*_):
            print('Received signal to stop')
            raise KeyboardInterrupt
        signal.signal(signal.SIGBREAK, interrupt_application)

    try:
        asyncio.run(run_agent(parsed_args))
    except KeyboardInterrupt:
        print('agent finished')


async def run_agent(parsed_args):
    agent_id = AgentID(parsed_args.root_id, parsed_args.id)
    logger = logging.getLogger()
    logger_setup.set_to_rotate(logger,
                               level=logging.INFO,
                               file_name_prefix=f'agent_{agent_id}')
    environment = load_agent_environment(parsed_args.id, parsed_args.config_file)
    agents_directory_helper = AgentsDirectoryHelper(address=parsed_args.agents_dir_addr,
                                                    port=parsed_args.agents_dir_port)

    if not environment:
        remove_logger_files(logger)
        raise ValueError('Required configuration files not present. Check again')

    clock = real_time_clock_factory()

    if parsed_args.comm_layer == 'raw':
        comm_layer_cls = RawCommunicationLayer
    elif parsed_args.comm_layer == 'REST':
        comm_layer_cls = RESTCommunicationLayer
    else:
        remove_logger_files(logger)
        raise ValueError('Invalid Communication Layer selected. Expect raw or REST')

    try:
        agent_handler = AgentHandler(environment=environment,
                                     clock=clock,
                                     agent_id=agent_id,
                                     agent_port=parsed_args.port,
                                     policies=parsed_args.policies,
                                     trigger_event_period=parsed_args.trigger_event_period,
                                     agents_directory_helper=agents_directory_helper,
                                     comm_layer_cls=comm_layer_cls)
    except RuntimeError as e:
        remove_logger_files(logger)
        sys.exit(e)

    await agent_handler.start()

    with create_pid_file():
        await clock.run()

    await agent_handler.finalize()


def build_argument_parser():
    parser = argparse.ArgumentParser(description='Instantiates an agent with default policies Info and TouchPointStatus')
    parser.add_argument('--root_id', type=int, required=True,
                        help='identifier of the agent creator')
    parser.add_argument('--id', type=int, required=True,
                        help='agent identifier')
    parser.add_argument('--port', type=int, default=8888,
                        help='agent listen port (default: %(default)s)')
    parser.add_argument('--policies', nargs='*', default=[],
                        help='policies that can handle events')
    parser.add_argument('--trigger_event_period', default=0, type=int,
                        help='period in seconds to trigger event')
    parser.add_argument('--agents_dir_addr', default='localhost',
                        help='agent directory server address')
    parser.add_argument('--agents_dir_port', default=1500, help='agent directory server port')
    parser.add_argument('--config_file', required=True,
                        help='configuration containing domain specific classes (sensors, actuators, and policies)')
    parser.add_argument('--comm_layer', required=True,
                        choices=['REST', 'raw'],
                        help='Type of communication layer used. Options: REST or raw')
    return parser


if __name__ == '__main__':
    main()
    sys.exit(0)
