#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging.config
from braincube.bc_connector.config_handler import config_setup_ok
from braincube.bc_connector.pandas_retriever import PandasRetriever
from braincube.bc_connector.raw_retriever import RawRetriever

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class Connector:
    def __init__(self, retriever, oauth2_access_token):
        self.__retriever = retriever
        self.__oauth2_access_token = oauth2_access_token

    def get_braincube_list(self):
        """
        :return: The list of available Braincube
        """
        return self.__retriever.get_braincube_list()

    def get_braincube(self, braincube_name):
        """
        :param braincube_name: a string with a braincube name
        :return: a braincube object, useful to access memorybases
        """
        return self.__retriever.get_braincube(braincube_name)

    def get_token(self):
        """
        :return: the oauth2 access token
        """
        return self.__oauth2_access_token


def get_data_collector(oauth2_acces_token=None, format_type='pandas'):
    """
    :param oauth2_acces_token: an OAuth2 access token can be specified. If none is set,
    :param format_type: 'raw' to return a connector working with plain python object, otherwise and by default return a connector working with pandas dataframe.
    :return: A connector allowing to access your braincube.
    """
    if config_setup_ok():
        # Function called by the user to access to flask_the python API
        # if the user call this function with a token, check it's validity and return an object object to manipulate the API
        logger.info("Initializing braincube data collector...")
        from braincube.bc_connector.tokensHandler import retrieve_tokens
        oauth2_acces_token, sso_token = retrieve_tokens(oauth2_acces_token)

        if format_type == 'raw':
            retriever = RawRetriever(sso_token['token'], sso_token['accessList'])
        else:
            retriever = PandasRetriever(sso_token['token'], sso_token['accessList'])

        return Connector(retriever, oauth2_acces_token)
