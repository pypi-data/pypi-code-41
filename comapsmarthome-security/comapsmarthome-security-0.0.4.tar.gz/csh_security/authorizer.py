import logging
import os

import psycopg2
import psycopg2.extras

from functools import reduce
from csh_security.user import User


def extract_user_id(api_gateway_event):
    user = extract_user(api_gateway_event)
    return user.id


def extract_user(api_gateway_event):
    oidc_user = api_gateway_event.get('requestContext', {}).get('authorizer', {})

    logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
    logging.getLogger().debug("authorizer : %s", oidc_user)

    id = oidc_user.get('sub', 'johndoe')
    roles = oidc_user['roles'].split(',')
    if len(roles) == 1 and roles[0] == '':
        roles = []

    return User(id=id, roles=roles)


def required_roles(roles):
    def required_roles_decorator(func):
        def wrapper(event, context):
            user = extract_user(event)
            user_roles = user.roles
            if not user_roles:
                return _access_forbidden_response()

            for user_role in user_roles:
                if user_role in roles:
                    return func(event, context)

            logging.getLogger().debug("Role permission check failed for user %s", user.id)
            return _access_forbidden_response()

        return wrapper
    return required_roles_decorator


def check_user_access_to_housing(func):
    return check_user_access_wrapper(func, ['housing_id'], lambda params: _has_access_to_housing(params['user_id'], params['housing_id']))


def check_user_access_to_connected_object(func):
    return check_user_access_wrapper(func, ['serial_number'], lambda params: _has_access_to_connected_object(params['user_id'], params['serial_number']))


def check_user_access_wrapper(func, checker_params, access_checker):
    def wrapper(event, _context):
        if 'pathParameters' not in event or not reduce(lambda acc, el: acc and el in event['pathParameters'].keys(), checker_params, True):
            return _access_forbidden_response()

        user = extract_user(event)
        params = {p: event['pathParameters'][p] for p in checker_params}
        params['user_id'] = user.id

        if 'admin' in user.roles or access_checker(params):
            return func(event, _context)
        else:
            return _access_forbidden_response()

    return wrapper


def _access_forbidden_response():
    return {
        'statusCode': 403
    }


def _has_access_to_housing(user_id, housing_id):
    _get_logger().debug("User %s attempting to access to housing %s...", user_id, housing_id)
    query = "SELECT id, user_id from housing.housing where id = '{}'".format(housing_id)
    return _has_access_to_resource(user_id, query)


def _has_access_to_connected_object(user_id, serial_number):
    _get_logger().debug("User %s attempting to access to connected_object %s...", user_id, serial_number)
    query = """SELECT user_id from housing.housing 
                inner join housing.connected_object on housing.housing.id = housing.connected_object.housing_id 
                where housing.connected_object.serial_number = '{}'"""\
                .format(serial_number)
    return _has_access_to_resource(user_id, query)


def _has_access_to_resource(user_id, query):
    if user_id == 'johndoe' and os.environ.get('IS_LOCAL', 'false') == 'true':
        _get_logger().debug("Running locally, access granted!")
        return True

    resource = _execute_query(query)

    if resource is not None and resource['user_id'] == user_id:
        _get_logger().debug("Access granted!")
        return True
    else:
        _get_logger().debug("Access denied!")
        return False


def _execute_query(query):
    connection = psycopg2.connect(
        user=os.environ.get("AUTHORIZER_DB_USER", os.environ.get("DB_USER", "postgres")),
        password=os.environ.get("AUTHORIZER_DB_PASSWORD", os.environ.get("DB_PASSWORD", "postgres")),
        host=os.environ.get("AUTHORIZER_DB_HOST", os.environ.get("DB_HOST", "localhost")),
        port=os.environ.get("AUTHORIZER_DB_PORT", os.environ.get("DB_PORT", 5432)),
        database=os.environ.get("AUTHORIZER_DB_NAME", os.environ.get("DB_NAME", "postgres"))
    )
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(query)
    return cursor.fetchone()


def _get_logger():
    return logging.getLogger('authorizer')
