from sidecar.model.objects import AwsSidecarConfiguration, AzureSidecarConfiguration
from sidecar.services.metadata.sandbox_public_address_fetcher import SandboxMetadataFetcher


class SandboxVpcFetcher(SandboxMetadataFetcher):
    def __init__(self, config: AwsSidecarConfiguration):
        self.config = config

    def get_value(self) -> str:
        return self.config.virtual_network_id


class SandboxVirtualNetworkFetcher(SandboxMetadataFetcher):
    def __init__(self, config: AzureSidecarConfiguration):
        self.config = config

    def get_value(self) -> str:
        return self.config.virtual_network_id