"""
End-to-end tests expected to be run against a data registry server
"""

from simiotics.registry import clients, data_pb2
from simiotics.registry.data_pb2_grpc import DataRegistryStub
from simiotics.version import CLIENT_VERSION

def main(data_registry: DataRegistryStub) -> None:
    """
    Runs end-to-end tests against a fresh data registry instance
    """
    # List registered functions and check that none are returned
    request = data_pb2.ListSourcesRequest(
        version=CLIENT_VERSION,
        offset=0,
        num_items=1,
    )
    response = data_registry.ListSources(request)
    assert response.offset == request.offset
    assert response.num_items == request.num_items
    assert not response.sources

    # Register 10 sources and check that the responses are as expected
    source_registration_requests = []
    source_registration_responses = []
    for i in range(10):
        source = data_pb2.Source(
            id='source-{}'.format(i),
            source_type=data_pb2.Source.SOURCE_FS,
            data_access_spec='/tmp/source-{}'.format(i),
        )
        request = data_pb2.RegisterSourceRequest(
            version=CLIENT_VERSION,
            source=source
        )
        source_registration_requests.append(request)
        response = data_registry.RegisterSource(request)
        source_registration_responses.append(response)

    for request, response in zip(source_registration_requests, source_registration_responses):
        assert response.source is not None
        assert request.source.id == response.source.id
        assert request.source.source_type == response.source.source_type
        assert request.source.data_access_spec == response.source.data_access_spec

    # Attempt to register a duplicated source and check that an exception is raised
    errored_out = False
    try:
        data_registry.RegisterSource(source_registration_requests[-1])
    except:
        errored_out = True

    assert errored_out

    # List 2 sources starting at index 5 and check that the response is as expected
    request = data_pb2.ListSourcesRequest(
        version=CLIENT_VERSION,
        offset=5,
        num_items=2,
    )
    response = data_registry.ListSources(request)
    assert len(response.sources) == 2
    for i, source in enumerate(response.sources):
        assert source.id == source_registration_responses[5+i].source.id
        assert source.source_type == source_registration_responses[5+i].source.source_type
        assert source.data_access_spec == source_registration_responses[5+i].source.data_access_spec

    # Get the registered source with index 3 and check that the correct source is returned
    request = data_pb2.GetSourceRequest(
        version=CLIENT_VERSION,
        id=source_registration_responses[3].source.id
    )
    response = data_registry.GetSource(request)
    assert response.source is not None
    assert source_registration_responses[3].source.id == response.source.id
    assert source_registration_responses[3].source.source_type == response.source.source_type
    assert (
        source_registration_responses[3].source.data_access_spec == response.source.data_access_spec
    )

    # Update the registered source with index 3 and check that the response is as expected
    update_notes = 'test update'
    request = data_pb2.UpdateSourceRequest(
        version=CLIENT_VERSION,
        id=source_registration_responses[3].source.id,
        notes=update_notes
    )
    response = data_registry.UpdateSource(request)
    assert response.source is not None
    expected_source = source_registration_responses[3].source
    assert response.source.id == expected_source.id
    assert response.source.source_type == expected_source.source_type
    assert response.source.data_access_spec == expected_source.data_access_spec
    assert not expected_source.updates
    assert len(response.source.updates) == 1
    assert response.source.updates[0].notes == update_notes

    # Get the registered source and check that the response is as expected
    request = data_pb2.GetSourceRequest(
        version=CLIENT_VERSION,
        id=source_registration_responses[3].source.id
    )
    response = data_registry.GetSource(request)
    expected_source = source_registration_responses[3].source
    assert response.source.id == expected_source.id
    assert response.source.source_type == expected_source.source_type
    assert response.source.data_access_spec == expected_source.data_access_spec
    assert not expected_source.updates
    assert len(response.source.updates) == 1
    assert response.source.updates[0].notes == update_notes

    # Register data against the sources indexed 0 and 1 and check that the response stream is as
    # expected
    data_registration_requests = []
    data_registration_responses = []
    def data_generator():
        for i in range(100):
            datum = data_pb2.Datum(
                id='data-0-{}'.format(i),
                source=source_registration_responses[0].source,
                content='content-0-{}'.format(i),
            )
            request = data_pb2.RegisterDataRequest(
                version=CLIENT_VERSION,
                datum=datum
            )
            data_registration_requests.append(request)
            yield request

        for i in range(33):
            datum = data_pb2.Datum(
                id='data-1-{}'.format(i),
                source=source_registration_responses[1].source,
                content='content-1-{}'.format(i),
            )
            request = data_pb2.RegisterDataRequest(
                version=CLIENT_VERSION,
                datum=datum
            )
            data_registration_requests.append(request)
            yield request

    responses = data_registry.RegisterData(data_generator())
    for response in responses:
        data_registration_responses.append(response)
    assert len(data_registration_responses) == 133
    assert len(data_registration_requests) == len(data_registration_responses)
    for request, response in zip(data_registration_requests, data_registration_responses):
        assert not response.error
        assert request.datum.id == response.datum.id
        assert request.datum.source.id == response.datum.source.id
        assert request.datum.content == response.datum.content

    # Get data for the source indexed 0 and check that we get the right number of samples
    request = data_pb2.GetDataRequest(
        version=CLIENT_VERSION,
        source_id=source_registration_responses[0].source.id
    )
    responses = data_registry.GetData(request)
    responses_list = list(responses)
    assert len(responses_list) == 100

    # Get data for the source indexed 1 and check that we get the right number of samples
    request = data_pb2.GetDataRequest(
        version=CLIENT_VERSION,
        source_id=source_registration_responses[1].source.id
    )
    responses = data_registry.GetData(request)
    responses_list = list(responses)
    assert len(responses_list) == 33

    # Get specific data for the source indexed 0, as well as (erroneously a sample from the source
    # indexed 1); verify that we only get the requested samples from the source indexed 0
    request = data_pb2.GetDataRequest(
        version=CLIENT_VERSION,
        source_id=source_registration_responses[0].source.id,
        ids=(
            [response.datum.id for response in data_registration_responses[:5]]
            + [data_registration_responses[-1].datum.id]
        )
    )
    responses = data_registry.GetData(request)
    responses_list = list(responses)
    assert len(responses_list) == 5
    assert (
        tuple(set(response.datum.source.id for response in responses_list))
        == (source_registration_responses[0].source.id,)
    )
    assert (
        tuple(sorted([response.datum.id for response in responses_list]))
        == tuple(sorted([response.datum.id for response in data_registration_responses[:5]]))
    )

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('End-to-end tests for data registry servers and clients')
    parser.add_argument(
        '-a',
        '--address',
        default='0.0.0.0:7010',
        help='Address (host and port) of the data registry server to test against',
    )

    args = parser.parse_args()

    data_registry_client = clients.data_registry_client(args.address)

    main(data_registry_client)
