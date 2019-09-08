from sidecar.azure_clp.azure_clients import AzureClientsManager
from sidecar.model.objects import AzureSidecarConfiguration
from sidecar.services.metadata.sandbox_public_address_fetcher import SandboxMetadataFetcher


class AzureVirtualNetworkFetcher(SandboxMetadataFetcher):
    def __init__(self, config: AzureSidecarConfiguration,  clients_manager: AzureClientsManager):
        self.config = config
        self.clients_manager = clients_manager

    def get_value(self) -> str:
        rg_name = self.config.production_id or self.config.sandbox_id
        vnet = self.clients_manager.network_client\
            .virtual_networks.get(resource_group_name=rg_name,
                                  virtual_network_name=self.config.vnet_name)
        return vnet.id