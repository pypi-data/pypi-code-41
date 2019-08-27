import pytest
from csh_security.authorizer import check_user_access_to_housing, check_user_access_to_connected_object, required_roles


@pytest.mark.parametrize("path_param, access_checker", [
    ({'housing_id': 'id'}, check_user_access_to_housing),
    ({'serial_number': 'aa01xxxxxxxx'}, check_user_access_to_connected_object)
])
def test_check_user_has_access_to_resource_should_return_403_because_user_does_not_have_access(mocker, path_param, access_checker):
    mocker.patch('csh_security.authorizer._execute_query').return_value = {'user_id': 'user_a'}
    event = {'pathParameters': path_param, 'requestContext': _user('user_b')}
    func_response = access_checker(lambda evt, _: {'statusCode': 204})
    assert func_response(event, None)['statusCode'] == 403


@pytest.mark.parametrize("access_checker", [
    check_user_access_to_housing,
    check_user_access_to_connected_object
])
def test_check_user_has_access_to_resource_should_return_403_because_param_is_missing_in_path(mocker, access_checker):
    mocker.patch('csh_security.authorizer._execute_query').return_value = {'user_id': 'user_a'}
    event = {'pathParameters': {}, 'requestContext': _user('user_b')}
    func_response = access_checker(lambda evt, _: {'statusCode': 200})
    assert func_response(event, None)['statusCode'] == 403


@pytest.mark.parametrize("path_param, access_checker", [
    ({'housing_id': 'id'}, check_user_access_to_housing),
    ({'serial_number': 'aa01xxxxxxxx'}, check_user_access_to_connected_object)
])
def test_check_user_has_access_to_resource_should_return_204_because_user_has_access(mocker, path_param, access_checker):
    mocker.patch('csh_security.authorizer._execute_query').return_value = {'user_id': 'user_a'}
    event = {'pathParameters': path_param, 'requestContext': _user('user_a')}
    func_response = access_checker(lambda evt, _: {'statusCode': 204})
    assert func_response(event, None)['statusCode'] == 204


def test_required_roles_should_return_403_because_user_does_not_have_required_role():
    decorator = required_roles(['admin', 'customer_service'])
    func_response = decorator(lambda evt, _: {'statusCode': 200})

    event = {'requestContext': _user('user_a', ['customer'])}
    assert func_response(event, None)['statusCode'] == 403


def test_required_roles_should_return_200_because_user_has_one_of_required_roles():
    decorator = required_roles(['admin', 'customer_service'])
    func_response = decorator(lambda evt, _: {'statusCode': 200})

    event = {'requestContext': _user('user_a', ['customer_service'])}
    assert func_response(event, None)['statusCode'] == 200


def _user(user_id, roles=None):
    user = {'sub': user_id}
    if roles:
        user['roles'] = ','.join(roles)
    return {'authorizer': user}
