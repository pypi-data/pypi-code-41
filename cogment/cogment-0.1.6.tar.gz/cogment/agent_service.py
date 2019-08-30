from abc import ABC, abstractmethod

from types import SimpleNamespace
from typing import Dict

from cogment.api.agent_pb2_grpc import AgentServicer

from cogment.api.agent_pb2 import (
     AgentStartReply, AgentDecideReply, AgentRewardReply, AgentEndReply)

from cogment.utils import list_versions
from cogment.trial import Trial
from cogment.delta_encoding import DecodeObservationData


class Agent(ABC):
    VERSIONS: Dict[str, str]

    def __init__(self, trial: Trial):
        self.trial = trial

    def end(self):
        pass

    @abstractmethod
    def reward(self, reward):
        pass

    @abstractmethod
    def decide(self, observation):
        pass


def trial_key(trial_id, actor_id):
    return f'{trial_id}_{actor_id}'


class AgentService(AgentServicer):
    def __init__(self, agent_class, settings):
        assert issubclass(agent_class, Agent)

        # We will be managing a pool of agents, keyed by their session id.
        self._agents: Dict[str, SimpleNamespace] = {}
        self._agent_class = agent_class
        self.settings: ModuleType = settings

        try:
            self._actor_class = agent_class.actor_class
        except AttributeError as err:
            raise AttributeError("You must define an actor_class property to your Agent")

        print("Agent Service started")

    def Start(self, request, context):
        try:
            trial_id = request.trial_id
            actor_id = request.actor_id

            if not trial_id:
                raise Exception("No trial_id provided")

            # Sanity check: We should only ever create a session once.
            if trial_id in self._agents:
                raise Exception("session already exists")

            trial = Trial(trial_id, self.settings)

            # Instantiate the fresh agent
            instance = self._agent_class(trial)

            self._agents[trial_key(trial_id, actor_id)] = SimpleNamespace(
                instance=instance, trial=trial, last_observation=None)

            reply = AgentStartReply()

            return reply
        except Exception as e:
            print(f'Start failure: {e}')
            raise

    def End(self, request, context):
        try:
            try:
                key = trial_key(request.trial_id, request.actor_id)
                data = self._agents[key]
                data.instance.end()
                del self._agents[key]
                return AgentEndReply()
            except KeyError as err:
                raise Exception("trial does not exists")
        except Exception as e:
            print(f'End failure: {e}')
            raise

    # The orchestrator is ready for the environemnt to move forward in time.
    def Decide(self, request, context):

        try:
            try:
                data = self._agents[trial_key(request.trial_id,
                                              request.actor_id)]
            except KeyError as err:
                raise Exception("trial does not exists")

            data.trial.tick_id = request.observation.tick_id
            data.last_observation = DecodeObservationData(
                self._agent_class.actor_class, request.observation.data, data.last_observation)

            action = data.instance.decide(data.last_observation)

            reply = AgentDecideReply()
            reply.action.content = action.SerializeToString()
            reply.feedbacks.extend(data.trial._get_all_feedback())

            return reply
        except Exception as e:
            print(f'Decide failure: {e}')
            raise

    def Reward(self, request, context):
        try:
            try:
                data = self._agents[trial_key(request.trial_id, request.actor_id)]
            except KeyError as err:
                raise Exception("trial does not exists")

            data.instance.reward(request.reward)

            reply = AgentRewardReply()

            return reply
        except Exception as e:
            print(f'Reward failure: {e}')
            raise

    def Version(self, request, context):
        try:
            return list_versions(self._agent_class)
        except Exception as e:
            print(f'Version failure: {e}')
            raise
