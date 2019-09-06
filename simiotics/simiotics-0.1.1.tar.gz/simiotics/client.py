"""
This module defines the Simiotics client class, which encodes the higher-level semantics for
interacting with simiotics services.
"""

import argparse
from typing import Optional

from .registry import data_pb2_grpc
from .registry import functions_pb2_grpc
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

def generate_argument_parser() -> argparse.ArgumentParser:
    """
    Generates an argparse argument parser which parses intialization values for the Simiotics client
    class from a string or from a list of strings (as one would receive from the command line)

    Args: None

    Returns: argparse.ArgumentParser instance which parses initialization configuration for
    Simiotics objects
    """
    parser = argparse.ArgumentParser('Simiotics')

    parser.add_argument(
        '--data-registry',
        default=None,
        help='Address for data registry gRPC server'
    )
    parser.add_argument(
        '--function-registry',
        default=None,
        help='Address for function registry gRPC server'
    )

    return parser

def client_from_args(args: argparse.Namespace) -> Simiotics:
    """
    Generates a Simiotics client from arguments parsed from the command line or from a string or
    list of strings (as accepted by argparse ArgumentParser instance parse_args methods).

    Args:
    args
        argparse namespace from which the attributes named as per the keyword arguments to the
        Simiotics __init__ method are used to initialize a Simiotics client

    Returns: Simiotic client instance created as per the specification implicit in args
    """
    client = Simiotics(
        data_registry=args.data_registry,
        function_registry=args.function_registry,
    )

    return client
