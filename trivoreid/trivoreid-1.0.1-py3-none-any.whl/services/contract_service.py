#!/usr/bin/env python
# coding: utf-8

import requests
import json
import logging

import trivoreid
import trivoreid.utils.service_utils as su
from trivoreid.exceptions import TrivoreIDSDKException, TrivoreIDException
from trivoreid.models.page import Page
from trivoreid.models.contract import (Contract,
                                       Party,
                                       Signer,
                                       PartyContact,
                                       Appendix,
                                       ContractContent)

class ContractService(object):
    '''
    Class to wrap Trivore ID Contracts API
    '''

    # Covered:
    _CONTRACTS = 'api/rest/v1/contract'
    _CONTRACT = 'api/rest/v1/contract/{}'
    _PARTIES = 'api/rest/v1/contract/{}/party'
    _PARTY = 'api/rest/v1/contract/{}/party/{}'
    _TERMINATE = 'api/rest/v1/contract/{}/actions/terminate'
    _FINALISE = 'api/rest/v1/contract/{}/actions/finalise'
    _ACTIONS = 'api/rest/v1/contract/{}/actions'
    _SIGNERS = 'api/rest/v1/contract/{}/party/{}/signer'
    _SIGNER = 'api/rest/v1/contract/{}/party/{}/signer/{}'
    _SIGN = 'api/rest/v1/contract/{}/actions/sign'
    _CONTACTS = 'api/rest/v1/contract/{}/party/{}/contact'
    _CONTACT = 'api/rest/v1/contract/{}/party/{}/contact/{}'
    _APPENDICES = 'api/rest/v1/contract/{}/appendix'
    _APPENDIX = 'api/rest/v1/contract/{}/appendix/{}'
    _CONTRACT_BODY = 'api/rest/v1/contract/{}/body'
    _APPENDIX_ORDER = 'api/rest/v1/contract/{}/appendix/order'
    _CONTRACT_BODY_FILE = 'api/rest/v1/contract/{}/body/file'
    _AX_FILE = 'api/rest/v1/contract/{}/appendix/{}/file'

    def __init__(self, credentials):
        self._server = credentials.server

        if credentials.oidc_client is None:
            self._session = requests
            self._auth = credentials.auth
        else:
            self._session = credentials.oidc_client
            self._auth = None

        self._header = credentials.access_token

    def get_all(self,
                filter_fields=None,
                start_index=0,
                count=100):
        '''Get the list of accessible contracts.
        Args:
            filter_fields (Filter) : filter out the result.
            start_index (int)      : 0-based pagination start index
            count (int)            : pagination page size, max 500
        Returns:
            Page with the pagination data and the list of accessible contracts.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        params = su.generate_parameters(filter_fields, start_index, count)
        uri = su.uri(self._server, self._CONTRACTS)
        response = self._session.get(uri, params=params,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} contracts'
                                .format(len(response.json()['resources'])))
            contracts = []
            for c in response.json()['resources']:
                contracts.append(Contract(c))
            page = Page(response.json(), contracts)
            return page
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create(self, contract):
        '''Create new contract.
        Args:
            contract (Contract): contract to create.
        Returns:
            New contract object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Contract is wrong.
        '''
        if type(contract) != trivoreid.models.contract.Contract:
            raise TrivoreIDSDKException('Contract type is wrong!')

        uri = su.uri(self._server, self._CONTRACTS)
        response = self._session.post(uri,
                                     json=contract.serialize(),
                                     headers=self._header,
                                     auth=self._auth)

        if response.status_code == 201:
            contr = Contract(response.json())
            logging.info('Successfully created contract with id {}'.format(
                                contr.id))
            return contr
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get(self, contractId):
        '''Get a single contract by id.
        Args:
            contractId (str) : contract's unique identifier
        Returns:
            A contract.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CONTRACT).format(contractId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found contract with id {}'.format(contractId))
            return Contract(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update(self, contract, contractId=None):
        '''Update existing contract.
        Args:
            contract (Contract)  : contract to modify.
            contractId (str)     : if None, then contract ID from
                                   the Contract object will be used.
        Returns:
            Modified contract object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the contract is wrong.
        '''
        if type(contract) != trivoreid.models.contract.Contract:
            raise TrivoreIDSDKException('Contract type is wrong!')

        if contractId is None:
            contractId = contract.id

        uri = su.uri(self._server, self._CONTRACT).format(contractId)
        response = self._session.put(uri,
                                    json=contract.serialize(),
                                    headers=self._header,
                                    auth=self._auth)

        if response.status_code is 200:
            contr = Contract(response.json())
            logging.info('Successfully modified contract with the id {}'
                        .format(contr.id))
            return contr
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete(self, contractId):
        '''Delete contract by id.
        Args:
            contractId (str) : contract's unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._CONTRACT).format(contractId)
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted contract with id {}'
                                                .format(contractId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_allowed_actions(self, contractId):
        '''
        Get Contract's allowed actions.
        Args:
            contractId (str) : contract's unique identifier
        Returns:
            The dictionary containing allowed actions.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._ACTIONS).format(contractId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found allowed actions for the contract {}'
                                                .format(contractId))
            return response.json()
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def finalise(self, contractId):
        '''
        Finalise the Contract.
        Args:
            contractId (str) : contract's unique identifier
        Returns:
            The Contract object.
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._FINALISE).format(contractId)
        response = self._session.post(uri, headers=self._header,
                                           auth=self._auth)

        if response.status_code == 200:
            contr = Contract(response.json())
            logging.info('Successfully finalised contract with id {}'.format(
                                contr.id))
            return contr
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def terminate(self, contractId, reason=None):
        '''
        Terminate the Contract.
        Args:
            contractId (str) : contract's unique identifier
            reason (str)     : Reason to terminate the contract. Optional.
        Returns:
            The Contract object.
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        params = {}
        if (reason != None):
            params['reason'] = reason

        uri = su.uri(self._server, self._TERMINATE).format(contractId)
        response = self._session.post(uri, params=params,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code == 200:
            contr = Contract(response.json())
            logging.info('Successfully terminated contract with id {}'.format(
                                contr.id))
            return contr
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def sign(self, contractId):
        '''
        Sign the Contract.
        Args:
            contractId (str) : contract's unique identifier
        Returns:
            The Contract object.
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._SIGN).format(contractId)
        response = self._session.post(uri, headers=self._header,
                                           auth=self._auth)

        if response.status_code == 200:
            contract = Contract(response.json())
            logging.info('Successfully signed contract with id {}'.format(
                                contract.id))
            return contract
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_parties(self, contractId):
        '''Get the list of parties of the contract.
        Args:
            contractId (str) : target contract ID
        Returns:
            List of parties.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._PARTIES).format(contractId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} parties'.format(len(response.json())))
            parties = []
            for p in response.json():
                parties.append(Party(p))
            return parties
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_party(self, contractId, party):
        '''Create new party.
        Args:
            contractId (str) : target contract ID
            party (Party)    : party to create.
        Returns:
            New party object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Contract is wrong.
        '''
        if type(party) != trivoreid.models.contract.Party:
            raise TrivoreIDSDKException('Party type is wrong!')

        uri = su.uri(self._server, self._PARTIES).format(contractId)
        response = self._session.post(uri,
                                      json=party.serialize(),
                                      headers=self._header,
                                      auth=self._auth)

        if response.status_code == 200:
            prt = Party(response.json())
            logging.info('Successfully created party with id {}'.format(prt.id))
            return prt
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_party(self, contractId, partyId):
        '''Get a single party from the contract.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party ID
        Returns:
            A party.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._PARTY).format(contractId, partyId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found party wiht id {} from contract {}'
                                            .format(contractId, partyId))
            return Party(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_party(self, contractId, party, partyId=None):
        '''Update existing party of the contract.
        Args:
            party (Party)        : party to modify.
            contractId (str)     : contract's unique identifier.
            partyId (str)        : party's unique identifier.
        Returns:
            Modified contract object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the contract is wrong.
        '''
        if type(party) != trivoreid.models.contract.Party:
            raise TrivoreIDSDKException('Party type is wrong!')

        if partyId is None:
            partyId = party.id

        uri = su.uri(self._server, self._PARTY).format(contractId, partyId)
        response = self._session.put(uri,
                                    json=party.serialize(),
                                    headers=self._header,
                                    auth=self._auth)

        if response.status_code is 200:
            prt = Party(response.json())
            logging.info('Successfully modified party with the id {}'
                        .format(prt.id))
            return prt
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_party(self, contractId, partyId):
        '''Delete party by id.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party's unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = su.uri(self._server, self._PARTY).format(contractId, partyId)
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted party with id {}'
                                                        .format(partyId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_party_signers(self, contractId, partyId):
        '''Get the party signers.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party's unique identifier
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._SIGNERS).format(contractId, partyId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} signers'.format(len(response.json())))
            signers = []
            for s in response.json():
                signers.append(Signer(s))
            return signers
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_party_signer(self, contractId, partyId, signer):
        '''Create new signer.
        Args:
            contractId (str) : target contract ID
            partyId (str)    : party's unique identifier
            signer (Signer)  : signer to create.
        Returns:
            New party object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Contract is wrong.
        '''
        if type(signer) != trivoreid.models.contract.Signer:
            raise TrivoreIDSDKException('Signer type is wrong!')

        uri = su.uri(self._server, self._SIGNERS).format(contractId, partyId)
        response = self._session.post(uri,
                                    json=signer.serialize(),
                                    headers=self._header,
                                    auth=self._auth)

        if response.status_code == 200:
            s = Signer(response.json())
            logging.info('Successfully created signer with id {}'.format(s.id))
            return s
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_party_signer(self, contractId, partyId, signerId):
        '''Get a single signer of the party.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party ID
            signerId (str)   : signer ID
        Returns:
            A signer.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = (su.uri(self._server, self._SIGNER)
                                         .format(contractId, partyId, signerId))
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found signer wiht id {} from party {}'
                                        .format(signerId, partyId))
            return Signer(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_party_signer(self, contractId, partyId, signer, signerId=None):
        '''Update existing party of the contract.
        Args:
            signer (Signer)      : signer to modify.
            contractId (str)     : contract's unique identifier.
            partyId (str)        : party's unique identifier.
            signerId (str)       : signer ID
        Returns:
            Modified contract object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the contract is wrong.
        '''
        if type(signer) != trivoreid.models.contract.Signer:
            raise TrivoreIDSDKException('Signer type is wrong!')

        if signerId is None:
            signerId = signer.id

        uri = (su.uri(self._server, self._SIGNER)
                                         .format(contractId, partyId, signerId))
        response = self._session.put(uri,
                                     json=signer.serialize(),
                                     headers=self._header,
                                     auth=self._auth)

        if response.status_code is 200:
            s = Signer(response.json())
            logging.info('Successfully modified signer with the id {}'
                        .format(s.id))
            return s
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_party_signer(self, contractId, partyId, signerId):
        '''Delete party signer.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party's unique identifier
            signerId (str)   : signer ID
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = (su.uri(self._server, self._SIGNER)
                                         .format(contractId, partyId, signerId))
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted signer with id {} from party {}'
                                        .format(signerId, partyId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_party_contacts(self, contractId, partyId):
        '''Get the party contacts.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party's unique identifier
        Returns:
            List of contacts.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CONTACTS).format(contractId, partyId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} contacts'.format(len(response.json())))
            contacts = []
            for c in response.json():
                contacts.append(PartyContact(c))
            return contacts
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_party_contact(self, contractId, partyId, contact):
        '''Create new contact.
        Args:
            contractId (str)        : target contract ID
            partyId (str)           : party's unique identifier
            contact (PartyContact)  : contact to create.
        Returns:
            New contact object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Contract is wrong.
        '''
        if type(contact) != trivoreid.models.contract.PartyContact:
            raise TrivoreIDSDKException('PartyContact type is wrong!')

        uri = su.uri(self._server, self._CONTACTS).format(contractId, partyId)
        response = self._session.post(uri,
                                      json=contact.serialize(),
                                      headers=self._header,
                                      auth=self._auth)

        if response.status_code == 200:
            c = PartyContact(response.json())
            logging.info('Successfully created contact with id {}'.format(c.id))
            return c
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_party_contact(self, contractId, partyId, contactId):
        '''Get a single signer of the party.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party ID
            contactId (str)  : contact ID
        Returns:
            A contact.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = (su.uri(self._server, self._CONTACT)
                                        .format(contractId, partyId, contactId))
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found contact wiht id {} from party {}'
                                        .format(contactId, partyId))
            return PartyContact(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_party_contact(self,
                             contractId,
                             partyId,
                             contact,
                             contactId=None):
        '''Update existing party of the contract.
        Args:
            contact (PartyContact)    : contact to modify.
            contractId (str)          : contract's unique identifier.
            partyId (str)             : party's unique identifier.
            contactId (str)           : signer ID
        Returns:
            Modified contact object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the contract is wrong.
        '''
        if type(contact) != trivoreid.models.contract.PartyContact:
            raise TrivoreIDSDKException('PartyContact type is wrong!')

        if contactId is None:
            contactId = contact.id

        uri = (su.uri(self._server, self._CONTACT)
                                        .format(contractId, partyId, contactId))
        response = self._session.put(uri,
                                     json=contact.serialize(),
                                     headers=self._header,
                                     auth=self._auth)

        if response.status_code is 200:
            c = PartyContact(response.json())
            logging.info('Successfully modified contact with the id {}'
                        .format(c.id))
            return c
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_party_contact(self, contractId, partyId, contactId):
        '''Delete party contact.
        Args:
            contractId (str) : contract's unique identifier
            partyId (str)    : party's unique identifier
            contactId (str)  : contact ID
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = (su.uri(self._server, self._CONTACT)
                                        .format(contractId, partyId, contactId))
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted contact with id {} from party {}'
                                        .format(contactId, partyId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_all_appendices(self, contractId):
        '''Get the party appendices.
        Args:
            contractId (str) : contract's unique identifier
        Returns:
            List of contract's appendices.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._APPENDICES).format(contractId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found {} appendices'.format(len(response.json())))
            appendices = []
            for a in response.json():
                appendices.append(Appendix(a))
            return appendices
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def create_appendix(self, contractId, appendix):
        '''Create new party.
        Args:
            contractId (str)    : target contract ID
            appendix (Appendix) : appendix to create.
        Returns:
            New appendix object.
        Raises:
            TrivoreIDException    if the status code is not 201.
            TrivoreIDSDKException if the type of the Contract is wrong.
        '''
        if type(appendix) != trivoreid.models.contract.Appendix:
            raise TrivoreIDSDKException('Appendix type is wrong!')

        uri = su.uri(self._server, self._APPENDICES).format(contractId)
        response = self._session.post(uri,
                                      json=appendix.serialize(),
                                      headers=self._header,
                                      auth=self._auth)

        if response.status_code == 201:
            a = Appendix(response.json())
            logging.info('Successfully created appendix {}'.format(a.id))
            return a
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_appendix(self, contractId, appendixId):
        '''Get a single appendix from the contract.
        Args:
            contractId (str) : contract's unique identifier
            appendixId (str) : appendix ID
        Returns:
            An appendix.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = (su.uri(self._server, self._APPENDIX)
                                    .format(contractId, appendixId))
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found appendix wiht id {} from contract {}'
                                            .format(appendixId, contractId))
            return Appendix(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_appendix(self, contractId, appendix, appendixId=None):
        '''Update existing party of the contract.
        Args:
            appendix (Appendix)  : appendix to modify.
            contractId (str)     : contract's unique identifier.
            partyId (str)        : party's unique identifier.
        Returns:
            Modified appendix object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the contract is wrong.
        '''
        if type(appendix) != trivoreid.models.contract.Appendix:
            raise TrivoreIDSDKException('Appendix type is wrong!')

        if appendixId is None:
            appendixId = appendix.id

        uri = (su.uri(self._server, self._APPENDIX)
                                    .format(contractId, appendixId))
        response = self._session.put(uri,
                                json=appendix.serialize(),
                                headers=self._header,
                                auth=self._auth)

        if response.status_code is 200:
            a = Appendix(response.json())
            logging.info('Successfully modified appendix with the id {}'
                        .format(a.id))
            return a
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_appendix(self, contractId, appendixId):
        '''Delete party by id.
        Args:
            contractId (str) : contract's unique identifier
            appendixId (str) : appendix unique identifier
        Raises:
            TrivoreIDException if the status code is not 204.
        '''
        uri = (su.uri(self._server, self._APPENDIX)
                                    .format(contractId, appendixId))
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code is 204:
            logging.info('Successfully deleted appendix with id {}'
                                        .format(appendixId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_contract_content(self, contractId):
        '''Get a contract content.
        Args:
            contractId (str) : contract's unique identifier
        Returns:
            A contract content.
        Raises:
            TrivoreIDException if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CONTRACT_BODY).format(contractId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code is 200:
            logging.info('Found content from contract with id {}'
                                                .format(contractId))
            return ContractContent(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def update_contract_content(self, contractId, content):
        '''Update contract content.
        Args:
            contract (ContractContent)  : contract to modify.
            contractId (str)            : if None, then contract ID from
                                          the Contract object will be used.
        Returns:
            Modified contract object.
        Raises:
            TrivoreIDException if the status code is not 200.
            TrivoreIDSDKException if the type of the contract is wrong.
        '''
        if type(content) != trivoreid.models.contract.ContractContent:
            raise TrivoreIDSDKException('ContractContent type is wrong!')

        uri = su.uri(self._server, self._CONTRACT_BODY).format(contractId)
        response = self._session.put(uri,
                                    json=content.serialize(),
                                    headers=self._header,
                                    auth=self._auth)

        if response.status_code is 200:
            logging.info(
                'Successfully modified content of the contract with the id {}'
                        .format(contractId))
            return ContractContent(response.json())
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def change_appendix_order(self, contractId, order):
        '''Change appendix order.
        Args:
            contractId (str)    : target contract ID
            order (list)        : ordered list of appendix IDs
        Returns:
            List of ordered appendices.
        Raises:
            TrivoreIDException    if the status code is not 201.
        '''
        uri = su.uri(self._server, self._APPENDIX_ORDER).format(contractId)
        response = self._session.post(uri, json=order,
                                           headers=self._header,
                                           auth=self._auth)

        if response.status_code == 200:
            logging.info(
            'Successfully changed order of appendices in contract with id {}'
                                    .format(contractId))
            appendices = []
            for a in response.json():
                appendices.append(Appendix(a))
            return appendices
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_appendix_file(self, contractId, appendixId):
        '''Get the appendix file.
        Args:
            contractId (str)    : target contract ID
            appendixId (str)    : target appendix ID
        Returns:
            A file (in bytes).
        Raises:
            TrivoreIDException    if the status code is not 200.
        '''
        uri = su.uri(self._server, self._AX_FILE).format(contractId, appendixId)
        response = self._session.get(uri, stream=True,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code == 200:
            logging.info(
                    'Successfully got the file from appendix with id {}'
                                    .format(appendixId))
            return response.content
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def upload_appendix_file(self, contractId, appendixId, file):
        '''Upload replacement appendix file contents.
        Args:
            contractId (str)    : target contract ID
            appendixId (str)    : target appendix ID
            file                : file (bytes) to upload.
        Raises:
            TrivoreIDException    if the status code is not 204.
        '''
        uri = su.uri(self._server, self._AX_FILE).format(contractId, appendixId)
        response = self._session.put(uri, data=file,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code == 204:
            logging.info(
                    'Successfully uploaded the file to appendix with id {}'
                                    .format(appendixId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_appendix_file(self, contractId, appendixId):
        '''Deletes an appendix with specified ID.
        Args:
            contractId (str)    : target contract ID
            appendixId (str)    : target appendix ID
        Raises:
            TrivoreIDException    if the status code is not 204.
        '''
        uri = su.uri(self._server, self._AX_FILE).format(contractId, appendixId)
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code == 204:
            logging.info(
                'Successfully deleted file from the appendix with id {}'
                                    .format(appendixId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def get_body_file(self, contractId):
        '''Get the contract content file.
        Args:
            contractId (str)    : target contract ID
        Returns:
            A file (in bytes).
        Raises:
            TrivoreIDException    if the status code is not 200.
        '''
        uri = su.uri(self._server, self._CONTRACT_BODY_FILE).format(contractId)
        response = self._session.get(uri, headers=self._header, auth=self._auth)

        if response.status_code == 200:
            logging.info('Successfully got the file from the contract {}'
                                    .format(contractId))
            return response.content
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def upload_body_file(self, contractId, file):
        '''Upload contract content file.
        Args:
            contractId (str)    : target contract ID
            file                : file (bytes) to upload.
        Raises:
            TrivoreIDException    if the status code is not 204.
        '''
        uri = su.uri(self._server, self._CONTRACT_BODY_FILE).format(contractId)
        response = self._session.put(uri, data=file,
                                          headers=self._header,
                                          auth=self._auth)

        if response.status_code == 204:
            logging.info('Successfully uploaded the file to the contract {}'
                                    .format(contractId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)

    def delete_body_file(self, contractId):
        '''Deletes a contract content file.
        Args:
            contractId (str)    : target contract ID
        Raises:
            TrivoreIDException    if the status code is not 204.
        '''
        uri = su.uri(self._server, self._CONTRACT_BODY_FILE).format(contractId)
        response = self._session.delete(uri, headers=self._header,
                                             auth=self._auth)

        if response.status_code == 204:
            logging.info('Successfully deleted file from the contract {}'
                                    .format(contractId))
        else:
            raise TrivoreIDException(su.error_response_message(response),
                                     response.status_code)
