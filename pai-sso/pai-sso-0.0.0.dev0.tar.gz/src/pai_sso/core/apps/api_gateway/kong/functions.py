import logging

import requests
from django.conf import settings

logger = logging.getLogger('api_gateway')


def get_consumer_id(user):
    consumer_id = str(user.id).replace('-', '_')

    if settings.CONSUMER_DOMAIN is not None:
        consumer_id += '@' + settings.CONSUMER_DOMAIN

    return consumer_id


def create_consumer(user):
    consumer_id = get_consumer_id(user)
    logger.info('creating apigw consumer for {}'.format(user.username))

    url = settings.APIGW_HOST + "/consumers/"
    data = {'username': consumer_id}

    r = requests.post(url, json=data)

    response_body = None
    status_code = r.status_code
    try:
        response_body = r.json()
    except:
        logger.info('Response ({}) has no payload'.format(status_code))

    logger.info('apigw response ({0}) {1}'.format(status_code, response_body))
    return status_code, response_body


def delete_consumer(user):
    consumer_id = get_consumer_id(user)
    logger.info('deleting apigw consumer for {}'.format(user.username))

    url = settings.APIGW_HOST + "/consumers/" + consumer_id

    r = requests.delete(url)

    response_body = None
    status_code = r.status_code
    try:
        response_body = r.json()
    except:
        logger.info('Response ({}) has no payload'.format(status_code))

    logger.info('apigw response ({0}) {1}'.format(status_code, response_body))
    return status_code, response_body


def create_consumer_jwt(user):
    consumer_id = get_consumer_id(user)
    logger.info('creating apigw consumer jwt for {}'.format(user.username))

    url = settings.APIGW_HOST + "/consumers/" + consumer_id + "/jwt/"
    data = {}

    r = requests.post(url, json=data)

    response_body = None
    status_code = r.status_code
    try:
        response_body = r.json()
    except:
        logger.info('Response ({}) has no payload'.format(status_code))

    logger.info('apigw response ({0}) {1}'.format(status_code, response_body))
    return status_code, response_body


def delete_consumer_jwt(user, jwt_id):
    consumer_id = get_consumer_id(user)
    logger.info('deleting apigw consumer jwt for {}'.format(user.username))

    url = settings.APIGW_HOST + "/consumers/" + consumer_id + "/jwt/" + jwt_id

    r = requests.delete(url)

    status_code = r.status_code

    logger.info('apigw response ({0}) {1}'.format(status_code, None))
    return r.status_code, None


def get_consumer_jwts(user):
    consumer_id = get_consumer_id(user)
    logger.info('getting apigw consumer jwts for {}'.format(user.username))

    url = settings.APIGW_HOST + "/consumers/" + consumer_id + "/jwt/"

    r = requests.get(url)

    response_body = None
    status_code = r.status_code
    try:
        response_body = r.json()
    except:
        logger.info('Response ({}) has no payload'.format(status_code))

    logger.info('apigw response ({0}) {1}'.format(status_code, response_body))
    return status_code, response_body


def create_consumer_acl(user, group_name=settings.DJANGO_SSO_CONSUMER_GROUP):
    consumer_id = get_consumer_id(user)
    logger.info('creating apigw consumer acl {} for {}'.format(group_name,
                                                               user.username))

    url = settings.APIGW_HOST + "/consumers/" + consumer_id + "/acls/"
    data = {"group": group_name}

    r = requests.post(url, json=data)

    response_body = None
    status_code = r.status_code
    try:
        response_body = r.json()
    except:
        logger.info('Response ({}) has no payload'.format(status_code))

    logger.info('apigw response ({0}) {1}'.format(status_code, response_body))
    return status_code, response_body


def delete_consumer_acl(user, group_name):
    consumer_id = get_consumer_id(user)
    logger.info('deleting apigw consumer acl {} for {}'.format(group_name,
                                                               user.username))

    url = settings.APIGW_HOST + "/consumers/" + consumer_id + "/acls/" + group_name

    r = requests.delete(url)

    status_code = r.status_code

    logger.info('apigw response ({0}) {1}'.format(status_code, None))
    return r.status_code, None
