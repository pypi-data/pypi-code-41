import logging
import re

import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger('ml-rmd.gcr')


class Gcr:
    GCR_PATTERN = r"((.*\.?)gcr\.io)/(.*)"

    ACCESS_TOKEN_URL = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token'
    ACCESS_TOKEN_HEADERS = {'Metadata-Flavor': 'Google'}

    LOGIN_USER = 'oauth2accesstoken'

    @classmethod
    def get_gcr_match(cls, image):
        return re.match(cls.GCR_PATTERN, image)

    @classmethod
    def get_access_token(cls):
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=10))

        try:
            response = session.get(cls.ACCESS_TOKEN_URL, headers=cls.ACCESS_TOKEN_HEADERS, timeout=1)
            response.raise_for_status()
        except requests.exceptions.RequestException as ex:
            logging.error('Unable to get access token for GCR login: %s', str(ex))
            return

        response_json = response.json()
        access_token = response_json['access_token']
        return '"{}"'.format(access_token)

    @classmethod
    def format_endpoint(cls, gcr_repo):
        return 'https://{}'.format(gcr_repo)
