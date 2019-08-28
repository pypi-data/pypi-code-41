from enum import Enum

from sidecar.services.metadata.sandbox_public_address_fetcher import SandboxMetadataFetcher


class SandboxMetadataMembers(str, Enum):
    PUBLIC_ADDRESS = "SandboxPublicAddress"
    VIRTUAL_NETWORK_ID = "VirtualNetworkId"


class SandboxMetadata:
    fetcher = {}

    def __init__(self):
        pass

    def register_fetcher(self, metadata_name: SandboxMetadataMembers, fetcher: SandboxMetadataFetcher):
        if metadata_name in self.fetcher:
            raise Exception(f"metadata '{metadata_name}' already registered")
        self.fetcher[metadata_name] = fetcher

    def get(self, metadata_name: SandboxMetadataMembers):
        fetcher: SandboxMetadataFetcher = self.fetcher.get(metadata_name, None)
        if not fetcher:
            return None
        return fetcher.get_value()
