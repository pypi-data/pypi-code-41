from alfa_sdk.common.base import BaseClient
from alfa_sdk.secrets import SecretsClient
from alfa_sdk.resources import (
    Algorithm,
    AlgorithmEnvironment,
    AlgorithmRelease,
    MetaUnit,
)


class AlgorithmClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secrets = SecretsClient(session=self.session)

    #

    def get_algorithm(self, algorithm_id):
        return Algorithm(algorithm_id, session=self.session)

    def get_environment(self, environment_id):
        return AlgorithmEnvironment(environment_id, session=self.session)

    def get_release(self, release_id):
        return AlgorithmRelease(release_id, session=self.session)

    def get_mass_customization_unit(self, environment_id, tag):
        return MetaUnit(environment_id, tag, session=self.session)

    #

    def get_algorithm_from_context(self):
        environment = self.get_environment_from_context()
        if environment is None:
            return None
        return environment.get_algorithm()

    def get_environment_from_context(self):
        if not self.session.context or "algorithmEnvironmentId" not in self.session.context:
            return None

        environment_id = self.session.context.get("algorithmEnvironmentId")
        return self.get_environment(environment_id)

    #

    def list_algorithms(self):
        params = {"teamId": self.user["teamId"]}
        return self.session.request(
            "get", "baas", "/api/Algorithms/getList", params=params
        )

    def list_environments(self, algorithm_id):
        algorithm = self.get_algorithm(algorithm_id)
        return algorithm.list_environments()

    def list_releases(self, environment_id):
        environment = self.get_environment(environment_id)
        return environment.list_releases()

    def list_mass_customization_units(self, environment_id):
        environment = self.get_environment(environment_id)
        return environment.list_mass_customization_units()

    #

    def invoke(self, algorithm_id, environment, problem, **kwargs):
        return self.session.invoke(algorithm_id, environment, problem, **kwargs)

    def deploy(self, algorithm_id, environment, version, file_path, **kwargs):
        algorithm = self.get_algorithm(algorithm_id)
        environment = algorithm.get_environment(environment)
        return environment.deploy(version, file_path, **kwargs)
