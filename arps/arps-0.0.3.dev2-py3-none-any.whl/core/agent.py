import logging
from abc import abstractmethod
from typing import List

from arps.core.actuator_container import ActuatorContainer
from arps.core.agent_id_manager import AgentID
from arps.core.communication_layer import CommunicableEntity
from arps.core.sensor_container import SensorContainer


class Agent(CommunicableEntity):
    '''
    Base class for agents

    An agent has two list of touchpoints available: sensors and actuators
    '''

    def __init__(self, **kwargs):
        '''
        Keyword parameters:
        - sensors: list of sensors to be read
        - actuators: list of actuators to be controlled
        '''

        sensors = kwargs.pop('sensors')
        actuators = kwargs.pop('actuators')
        self._environment = kwargs.pop('environment')
        self._sensor_container = SensorContainer(sensors if sensors else [])
        self._actuator_container = ActuatorContainer(actuators if actuators else [])
        self._related_agents = set()
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__(**kwargs)

        assert isinstance(self.identifier, AgentID)

    def include_as_related(self, agent_id: AgentID):
        assert isinstance(agent_id, AgentID)

        self._related_agents.add(agent_id)

    def remove_as_related(self, agent_id: AgentID):
        assert isinstance(agent_id, AgentID)

        self._related_agents.remove(agent_id)

    @property
    def related_agents(self):
        return frozenset(self._related_agents)

    def sensors(self) -> List[str]:
        '''
        Returns a list of available sensors
        '''
        return self._sensor_container.categories()

    def actuators(self) -> List[str]:
        '''
        Returns a list of available actuators
        '''
        return self._actuator_container.categories()

    def update_touchpoints(self, sensors, actuators):

        self.logger.debug('updating with sensors {}'.format(sensors))
        self.logger.debug('updating with actuators {}'.format(actuators))

        sensors = [self._environment.sensor(sensor_id) for sensor_id in sensors]
        actuators = [self._environment.actuator(actuator_id) for actuator_id in actuators]

        self._sensor_container.add(sensors)
        self._actuator_container.add(actuators)

    def read_sensor(self, sensor_id):
        return self._sensor_container.read(sensor_id)

    def read_actuator(self, actuator_id):
        return self._actuator_container.read(actuator_id)

    def modify_actuator(self, actuator_category, **actuator_attributes):
        return self._actuator_container.set(actuator_category, **actuator_attributes)

    @abstractmethod
    async def run(self):
        '''Execute control loop
        '''


class _AgentImplementation(Agent):
    '''
    Responsible to run process.

    created by agent_factory.create_agent.

    When created a single process is added. This process will take care of the upper layer logic
    while this class will handle host stuff
    '''

    def __init__(self, **kwargs):
        self._process = None
        self._metrics_logger = kwargs.pop('metrics_logger')
        super().__init__(**kwargs)

    @property
    def process(self):
        return self._process

    async def receive(self, message):
        self.logger.debug('agent %s received message ', self.identifier)
        self._process.receive(message)
        self._metrics_logger.update_number_of_messages()

    @property
    def metrics_logger(self):
        return self._metrics_logger

    async def run(self):
        self.logger.debug(f'running agent {self.identifier}')
        await self._process.run()

    def _add_process(self, process):
        process.host = self
        self._process = process
        self._process.logger = logging.getLogger('Agent_{}_Process'.format(self.identifier))

    def __repr__(self):
        return f'Agent(identifier={self.identifier}, policies={self.process!r})'

    def __str__(self):
        return 'Agent {}'.format(self.identifier)
