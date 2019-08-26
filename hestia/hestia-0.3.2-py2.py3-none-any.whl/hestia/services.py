HEADERS_CLI_VERSION = 'X_POLYAXON_CLI_VERSION'
HEADERS_CLIENT_VERSION = 'X_POLYAXON_CLIENT_VERSION'
HEADERS_INTERNAL = 'X_POLYAXON_INTERNAL'
HEADERS_OPERATOR = 'X_POLYAXON_OPERATOR'


class InternalServices(object):  # noqa
    DOCKERIZER = 'dockerizer'
    INITIALIZER = 'initializer'
    SIDECAR = 'sidecar'
    HELPER = 'helper'
    RUNNER = 'runner'
    CONTROLLER = 'controller'

    VALUES = {
        DOCKERIZER,
        INITIALIZER,
        SIDECAR,
        HELPER,
        RUNNER,
        CONTROLLER
    }
