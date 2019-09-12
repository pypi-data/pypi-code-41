"""
This module defines the Simiotics client class, which encodes the higher-level semantics for
interacting with simiotics services.
"""

import argparse
import os
from typing import Optional

from .registry import data_pb2_grpc
from .registry import functions_pb2_grpc
from .registry.clients import data_registry_client, function_registry_client
from . import version

# pylint: disable=too-few-public-methods
class Simiotics:
    """
    Python representation of the simiotics platform. It is composed of clients for each of the
    individual services that comprise the platform.

    This class does nothing more than aggregate the different services. A user may use the
    appropriate component member of a Simiotics object to realize their desired behaviour against
    the platform.
    """
    def __init__(
            self,
            data_registry: Optional[data_pb2_grpc.DataRegistryStub] = None,
            function_registry: Optional[functions_pb2_grpc.FunctionRegistryStub] = None,
        ) -> None:
        """
        Creates a Simiotics instance representing one specific configuration of backends.

        Args:
        data_registry
            Data registry client (as generated, for example, by
            registry.clients.data_registry_client)
        function_registry
            Function registry client (as generated, for example, by
            registry.clients.function_registry_client)

        Returns: None
        """
        # self.version contains just the semantic version of this Simiotics client library
        self.version = version.VERSION
        # self.client_version specifies the version string that should be passed with gRPC requests
        # made by this client library
        self.client_version = version.CLIENT_VERSION

        self.data_registry = data_registry
        self.function_registry = function_registry
# pylint: enable=too-few-public-methods

def client_from_env() -> Simiotics:
    """
    Generates a Simiotics client instance using environment variables to populate its members.

    Accepts the following environment variables:
    1. SIMIOTICS_DATA_REGISTRY
    2. SIMIOTICS_FUNCTION_REGISTRY

    Args: None

    Returns: Simiotics client with specified members populated
    """
    data_registry_address = os.environ.get('SIMIOTICS_DATA_REGISTRY')
    data_registry = None
    if data_registry_address is not None:
        data_registry = data_registry_client(data_registry_address)

    function_registry_address = os.environ.get('SIMIOTICS_FUNCTION_REGISTRY')
    function_registry = None
    if function_registry_address is not None:
        function_registry = function_registry_client(function_registry_address)

    client = Simiotics(data_registry=data_registry, function_registry=function_registry)

    return client
