#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import os

import pytest
from ocean_keeper.contract_handler import ContractHandler
from ocean_keeper.web3_provider import Web3Provider
from web3 import HTTPProvider, Web3
from ocean_keeper.keeper import Keeper

from tests.resources.helper_functions import (
    get_consumer_account,
    get_publisher_account
)


def get_keeper_url():
    if os.getenv('KEEPER_URL'):
        return os.getenv('KEEPER_URL')
    return 'http://localhost:8545'


@pytest.fixture(autouse=True)
def setup_all():
    Web3Provider.get_web3(get_keeper_url())
    ContractHandler.artifacts_path = os.path.expanduser('~/.ocean/keeper-contracts/artifacts')
    Keeper.get_instance(artifacts_path=ContractHandler.artifacts_path)


@pytest.fixture
def publisher_account():
    return get_publisher_account()


@pytest.fixture
def consumer_account():
    return get_consumer_account()


@pytest.fixture
def web3_instance():
    return Web3(HTTPProvider(get_keeper_url()))
