"""
End-to-end tests expected to be run against a function registry server
"""

from simiotics.registry import clients, functions_pb2
from simiotics.registry.functions_pb2_grpc import FunctionRegistryStub
from simiotics.version import CLIENT_VERSION

def main(function_registry: FunctionRegistryStub) -> None:
    """
    Runs end-to-end tests against a fresh function registry instance
    """
    # List registered functions and check that none are returned
    request = functions_pb2.ListRegisteredFunctionsRequest(
        version=CLIENT_VERSION,
        offset=0,
        num_items=1,
    )
    response = function_registry.ListRegisteredFunctions(request)
    assert response.offset == request.offset
    assert response.num_items == request.num_items
    assert not response.function_messages

    # Register 10 functions and check that the responses are as expected
    registration_requests = []
    registration_responses = []
    for i in range(10):
        request = functions_pb2.RegisterFunctionRequest(
            version=CLIENT_VERSION,
            function_message=functions_pb2.RegisteredFunction(
                key='function-{}'.format(i),
                code='dummy-code-{}'.format(i)
            )
        )
        registration_requests.append(request)
        response = function_registry.RegisterFunction(request)
        registration_responses.append(response)

    for request, response in zip(registration_requests, registration_responses):
        assert request.overwrite == response.overwrite
        assert response.function_message is not None
        assert request.function_message.key == response.function_message.key
        assert request.function_message.code == response.function_message.code

    # List 2 functions starting at index 5 and check that the response is as expected
    request = functions_pb2.ListRegisteredFunctionsRequest(
        version=CLIENT_VERSION,
        offset=5,
        num_items=2,
    )
    response = function_registry.ListRegisteredFunctions(request)
    assert len(response.function_messages) == 2
    for i, message in enumerate(response.function_messages):
        assert message.key == registration_responses[5+i].function_message.key
        assert message.code == registration_responses[5+i].function_message.code

    # Get the registered function with index 3 and check that the correct function is returned
    request = functions_pb2.GetRegisteredFunctionRequest(
        version=CLIENT_VERSION,
        key=registration_responses[3].function_message.key
    )
    response = function_registry.GetRegisteredFunction(request)
    assert response.function_message is not None
    assert response.function_message.key == registration_responses[3].function_message.key
    assert response.function_message.code == registration_responses[3].function_message.code

    # Delete the registered function with index 3 and check that the correct key is returned
    request = functions_pb2.DeleteRegisteredFunctionRequest(
        version=CLIENT_VERSION,
        key=registration_responses[3].function_message.key
    )
    response = function_registry.DeleteRegisteredFunction(request)
    assert response.key == registration_responses[3].function_message.key

    # Attempt to get the deleted function and check that an exception is raised
    request = functions_pb2.GetRegisteredFunctionRequest(
        version=CLIENT_VERSION,
        key=registration_responses[3].function_message.key
    )
    errored_out = False
    try:
        function_registry.GetRegisteredFunction(request)
    except:
        errored_out = True
    assert errored_out

    # List 2 functions starting at offset 3 and make sure that the response contains the two
    # functions indexed 4 and 5
    request = functions_pb2.ListRegisteredFunctionsRequest(
        version=CLIENT_VERSION,
        offset=3,
        num_items=2,
    )
    response = function_registry.ListRegisteredFunctions(request)
    assert len(response.function_messages) == 2
    for i, message in enumerate(response.function_messages):
        assert message.key == registration_responses[4+i].function_message.key
        assert message.code == registration_responses[4+i].function_message.code

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('End-to-end tests for function registry servers and clients')
    parser.add_argument(
        '-a',
        '--address',
        default='0.0.0.0:7011',
        help='Address (host and port) of the function registry server to test against',
    )

    args = parser.parse_args()

    function_registry_client = clients.function_registry_client(args.address)

    main(function_registry_client)
