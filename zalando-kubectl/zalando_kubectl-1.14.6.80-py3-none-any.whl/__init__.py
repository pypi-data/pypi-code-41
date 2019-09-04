# This is replaced during release process.
# flake8: noqa
__version_suffix__ = '80'

APP_NAME = "zalando-kubectl"

KUBECTL_VERSION = 'v1.14.6'
KUBECTL_SHA512 = {
    'linux': '59624a0d591ba210f8db5bfa1ce7e0e5b3f5c2774fea356f7e459db5d245a18d72ffc315f82b2f97d0e283c269eeb40fd6eca683cd76b35fb83cfd3bc87cc911',
    'darwin': 'afed84639adb98fed7087a238415dbbbb6643ab7403ecea11a08ea8b230312551a5770de1b42fd0a379a4d0ca96e934f57ebf7c0ad5d11f282b75e381ef27c04'
}

STERN_VERSION = '1.10.0'
STERN_SHA256 = {
    'linux': 'a0335b298f6a7922c35804bffb32a68508077b2f35aaef44d9eb116f36bc7eda',
    'darwin': 'b91dbcfd3bbda69cd7a7abd80a225ce5f6bb9d6255b7db192de84e80e4e547b7'
}

APP_VERSION = KUBECTL_VERSION + "." + __version_suffix__
