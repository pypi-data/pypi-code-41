#!/usr/bin/env python
# coding: utf-8

import requests
import logging

import trivoreid.utils.service_utils as su
from trivoreid.models.paycard import Paycard, PanToken
from trivoreid.models.page import Page
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException

class PaycardService(object):
    '''
    Class to wrap Trivore ID /paycard API
    '''
    _PAYCARDS = 'api/rest/v1/user/{}/paycard'
    _PAYCARD = 'api/rest/v1/user/{}/paycard/{}'
    _PANTOKEN = 'api/rest/v1/user/{}/paycard/{}/pantoken/{}'
    _PANTOKENS = 'api/rest/v1/user/{}/paycard/{}/pantoken'

    def __init__(self, credentials):
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._auth_header = credentials.access_token

    def get_all(self, userId, filter_fields=None, start_index=0, count=100):
        '''Get list of Paycards of the user.
        Args:
            userId (str)           : user unique identifier
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of paycards.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        response = self._session.get(
                        su.uri(self._server, self._PAYCARDS.format(userId)),
                        params=params,
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} paycards'.format(len(response.json()['resources'])))
            cards = []
            for card in response.json()['resources']:
                cards.append(Paycard(card))
            page = Page(response.json(), cards)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, userId, paycard):
        '''Create new Paycard for the user.
        Args:
            userId (str)        : user's unique identifier'
            paycard (Paycard)   : paycard to create
        Returns:
            New paycard object.
        Raises:
            TrivoreIDSDKException if the type of the Paycard is wrong
            TrivoreIDException if the status code is not 201.
        '''
        if 'Paycard' not in str(type(paycard)):
            raise TrivoreIDSDKException('Paycard type is wrong')

        response = self._session.post(
                        su.uri(self._server, self._PAYCARDS.format(userId)),
                        json=paycard.serialize(),
                        headers=self._auth_header,
                        auth=self._auth)

        if response.status_code == 201:
            card = Paycard(response.json())
            logging.info('Successfully created paycard with id {}'.format(
                                card.id))
            return card
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, paycard, userId=None, cardId=None):
        '''Update existing user's paycard.
        Args:
            paycard (Paycard) : card to update.
            userId (str)      : user ID. If None, the ID defined in the paycard
                                will be used.
            cardId (str)      : card ID. If None, the ID defined in the paycard
                                will be used.
        Returns:
            Modified paycard object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the paycard is wrong.
        '''
        if 'Paycard' not in str(type(paycard)):
            raise TrivoreIDSDKException('Card type is wrong')

        if userId is None:
            userId = paycard.userId

        if cardId is None:
            cardId = paycard.id

        response = self._session.put(
                su.uri(self._server, self._PAYCARD).format(userId, cardId),
                json = paycard.serialize(),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 200:
            crd = Paycard(response.json())
            logging.info('Successfully modified card with the id {}'
                                                    .format(crd.id))
            return crd
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, userId, cardId):
        '''Get the single card by user and card ids.
        Args:
            userId (str) : user unique identifier
            cardId (str) : card unique identifier
        Returns:
            A paycard object.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(
                su.uri(self._server, self._PAYCARD).format(userId, cardId),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 200:
            logging.info('Found card with id {}'.format(cardId))
            return Paycard(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, userId, cardId):
        '''Delete card by id.
        Args:
            userId (str) : user unique identifier
            cardId (str) : card unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(
                su.uri(self._server, self._PAYCARD).format(userId, cardId),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted card with id {}'.format(cardId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_pan_tokens(self,
                           userId,
                           cardId,
                           filter_fields=None,
                           start_index=0,
                           count=100):
        '''Get list of PAN tokens of the paycard.
        Args:
            userId (str)           : user unique identifier
            cardId (str)           : card unique identifier
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of PAN tokens.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        response = self._session.get(
                su.uri(self._server, self._PANTOKENS.format(userId, cardId)),
                params=params,
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} pantokens'.format(
                                        len(response.json()['resources'])))
            tokens = []
            for token in response.json()['resources']:
                tokens.append(PanToken(token))
            page = Page(response.json(), tokens)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_pan_token(self, userId, cardId, pantoken):
        '''Create new PAN token for the user's paycard.
        Args:
            userId (str)           : user unique identifier
            cardId (str)           : card unique identifier
            pantoken (PanToken)    : PAN token to create
        Returns:
            New pantoken object.
        Raises:
            TrivoreIDException if the status code is not 201.
            TrivoreIDSDKException if the type of the pantoken is wrong.
        '''
        if 'PanToken' not in str(type(pantoken)):
            raise TrivoreIDSDKException('PanToken type is wrong')

        response = self._session.post(
                su.uri(self._server, self._PANTOKENS.format(userId, cardId)),
                json=pantoken.serialize(),
                headers=self._auth_header,
                auth=self._auth)

        if response.status_code == 201:
            token = PanToken(response.json())
            logging.info('Successfully created PAN token with id {}'.format(
                                token.id))
            return token
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_pan_token(self, userId, cardId, tokenId):
        '''Get the single pantoken.
        Args:
            userId (str)  : user unique identifier
            cardId (str)  : card unique identifier
            tokenId (str) : PAN token unique identifier
        Returns:
            A PAN token object.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        response = self._session.get(su.uri(self._server, self._PANTOKEN)
                                        .format(userId, cardId, tokenId),
                                     headers=self._auth_header,
                                     auth=self._auth)

        if response.status_code is 200:
            logging.info('Found pantoken with id {}'.format(tokenId))
            return PanToken(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_pan_token(self, userId, pantoken, cardId = None, tokenId = None):
        '''Update existing paycard's pantoken.
        Args:
            pantoken (PanToken)   : PAN token to update.
            userId (str)          : user unique identifier
            cardId (str)          : card unique identifier
            tokenId (str)         : PAN token unique identifier
        Returns:
            Modified PAN token object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the pantoken is wrong.
        '''
        if 'PanToken' not in str(type(pantoken)):
            raise TrivoreIDSDKException('PanToken type is wrong')

        if cardId is None:
            cardId = pantoken.paycardId

        if tokenId is None:
            tokenId = pantoken.id

        response = self._session.put(su.uri(self._server, self._PANTOKEN)
                                        .format(userId, cardId, tokenId),
                                     json = pantoken.serialize(),
                                     headers=self._auth_header,
                                     auth=self._auth)

        if response.status_code is 200:
            token = PanToken(response.json())
            logging.info('Successfully modified PAN token with the id {}'
                                            .format(token.id))
            return token
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_pan_token(self, userId, cardId, tokenId):
        '''Delete pantoken by id.
        Args:
            userId (str)    : user unique identifier
            cardId (str)    : card unique identifier
            tokenId (str)   : PAN token unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        response = self._session.delete(su.uri(self._server, self._PANTOKEN)
                                        .format(userId, cardId, tokenId),
                                        headers=self._auth_header,
                                        auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted PAN token with id {}'.format(tokenId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
