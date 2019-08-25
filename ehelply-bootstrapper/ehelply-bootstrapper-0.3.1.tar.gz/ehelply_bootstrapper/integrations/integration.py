class Integration:
    def __init__(self, name: str) -> None:
        self.name = name

    def init(self):
        pass

    def load(self):
        pass


class IntegrationManager:
    def __init__(self) -> None:
        self.integrations = []

    def register(self, integration: Integration):
        integration.init()
        self.integrations.append(integration)

    def load(self):
        for integration in self.integrations:
            integration.load()

    def get(self, name: str) -> Integration:
        for integration in self.integrations:
            if integration.name == name:
                return integration
