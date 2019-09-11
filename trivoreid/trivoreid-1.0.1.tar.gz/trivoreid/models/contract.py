#!/usr/bin/env python
# coding: utf-8

from trivoreid.exceptions import TrivoreIDSDKException

class Contract(object):
    '''
    The contract.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): contract fields
        Dictionary keys:
            'id' Internal id
            'termination' Readonly.
            'termOfNoticeDays' When termination has been initiated, the contract
                               will be in Under-Notice state this amount of days
                               until moving to Terminated state. If null or 0,
                               contract will move to Terminated state immediately.
            'terminationMode' Contract will terminate after this rule is met.
                              One of: AFTER_ALL_PARTIES_TERMINATE (default),
                              AFTER_SINGLE_PARTY_LEFT, AFTER_SINGLE_PARTY_TERMINATES
            'title'
            'version'
            'body' (ContractContent) Contract body or appendix content.
            'validFrom' Example: 2018-04-26T08:38:02.730Z.
            'validTo' Example: 2018-04-26T08:38:02.730Z.
            'code'
            'scope'
            'financialTerms' (FinancialTerms)
            'termsOfDelivery'
            'parties' (list of Party objects)
            'links'
            'stateEvents'  Readonly.
            'currentState' Readonly. One of: DRAFT, SIGNABLE, SIGNED, EXPIRED,
                           UNDER_NOTICE, TERMINATED, ARCHIVED.
            'currentStateChanged' Readonly.
            'appendices' Readonly.
            'addendumFor'
            'contractRefs'
            'frameworkAgreementRef'
            'ownerId' User ID of contract owner. Owner has right to edit the
                      contract while a draft, and to cancel it before it is
                      signed.
            'notes'
        '''
        self.id = data.pop('id', None)
        self.termination = data.pop('termination', None)
        self.termOfNoticeDays = data.pop('termOfNoticeDays', None)
        self.terminationMode = data.pop('terminationMode', None)
        self.title = data.pop('title', None)
        self.version = data.pop('version', None)
        self.validFrom = data.pop('validFrom', None)
        self.validTo = data.pop('validTo', None)
        self.code = data.pop('code', None)
        self.scope = data.pop('scope', None)
        self.termsOfDelivery = data.pop('termsOfDelivery', None)
        self.links = data.pop('links', [])
        self.stateEvents = data.pop('stateEvents', [])
        self.currentState = data.pop('currentState', None)
        self.currentStateChanged = data.pop('currentStateChanged', None)
        self.addendumFor = data.pop('addendumFor', None)
        self.contractRefs = data.pop('contractRefs', None)
        self.frameworkAgreementRef = data.pop('frameworkAgreementRef', None)
        self.ownerId = data.pop('ownerId', None)
        self.notes = data.pop('notes', None)

        self.parties = []
        for p in data.pop('parties', []):
            self.parties.append(Party(p))

        self.appendices = []
        for a in data.pop('appendices', []):
            self.appendices.append(Appendix(a))

        body = data.pop('body', ContractContent())
        if 'ContractContent' in str(type(body)):
            self.body = body
        elif type(body) is dict:
            self.body = ContractContent(body)
        else:
            raise TrivoreIDSDKException('body type is wrong!')

        financialTerms = data.pop('financialTerms', FinantialTerms())
        if 'FinantialTerms' in str(type(financialTerms)):
            self.financialTerms = financialTerms
        elif type(financialTerms) is dict:
            self.financialTerms = FinantialTerms(financialTerms)
        else:
            raise TrivoreIDSDKException('financialTerms type is wrong!')

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        parties = []
        for p in self.parties:
            parties.append(p.serialize())

        appendices = []
        for a in self.appendices:
            appendices.append(a.serialize())

        return {
            'id'                    : self.id,
            'termination'           : self.termination,
            'termOfNoticeDays'      : self.termOfNoticeDays,
            'terminationMode'       : self.terminationMode,
            'title'                 : self.title,
            'version'               : self.version,
            'body'                  : self.body.serialize(),
            'validFrom'             : self.validFrom,
            'validTo'               : self.validTo,
            'code'                  : self.code,
            'scope'                 : self.scope,
            'financialTerms'        : self.financialTerms.serialize(),
            'termsOfDelivery'       : self.termsOfDelivery,
            'parties'               : parties,
            'links'                 : self.links,
            'stateEvents'           : self.stateEvents,
            'currentState'          : self.currentState,
            'currentStateChanged'   : self.currentStateChanged,
            'appendices'            : appendices,
            'addendumFor'           : self.addendumFor,
            'contractRefs'          : self.contractRefs,
            'frameworkAgreementRef' : self.frameworkAgreementRef,
            'ownerId'               : self.ownerId,
            'notes'                 : self.notes
        }

class TerminationMode:
    '''
    Contract's termination mode.
    '''
    AFTER_ALL_PARTIES_TERMINATE = 'AFTER_ALL_PARTIES_TERMINATE'
    AFTER_SINGLE_PARTY_LEFT = 'AFTER_SINGLE_PARTY_LEFT'
    AFTER_SINGLE_PARTY_TERMINATES = 'AFTER_SINGLE_PARTY_TERMINATES'

class ContractContent(object):
    '''
    Contract body or appendix content.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): contract content fields
        Dictionary keys:
            'text'
            'externalFileRef' Reference link to a file on an external service.
            'hasInternalFile' Readonly.
            'internalFileType' Readonly.
        '''
        self.text = data.pop('text', None)
        self.externalFileRef = data.pop('externalFileRef', None)
        self.hasInternalFile = data.pop('hasInternalFile', False)
        self.internalFileType = data.pop('internalFileType', None)

    def serialize(self):
        return {
            'text'             : self.text,
            'externalFileRef'  : self.externalFileRef,
            'hasInternalFile'  : self.hasInternalFile,
            'internalFileType' : self.internalFileType
        }

class FinantialTerms(object):
    '''
    Finantial terms.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): finantial terms fields
        Dictionary keys:
            'paymentTerms'
            'billingTerms'
            'penaltyInterest'
        '''
        self.paymentTerms = data.pop('paymentTerms', None)
        self.billingTerms = data.pop('billingTerms', None)
        self.penaltyInterest = data.pop('penaltyInterest', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'paymentTerms'   : self.paymentTerms,
            'billingTerms'   : self.billingTerms,
            'penaltyInterest': self.penaltyInterest
        }

class Appendix(object):
    '''
    Contract's appendix.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): appendix fields.
        Dictionary keys:
            'id'               Readonly.
            'title'            Title of appendix or other content.
            'text'             Text content.
            'externalFileRef'  Reference link to a file on an external service.
            'hasInternalFile'  Readonly.
            'internalFileType' Readonly.
        '''
        self.id = data.pop('id', None)
        self.title = data.pop('title', None)
        self.text = data.pop('text', None)
        self.externalFileRef = data.pop('externalFileRef', None)
        self.hasInternalFile = data.pop('hasInternalFile', False)
        self.internalFileType = data.pop('internalFileType', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'id'                : self.id,
            'title'             : self.title,
            'text'              : self.text,
            'externalFileRef'   : self.externalFileRef,
            'hasInternalFile'   : self.hasInternalFile,
            'internalFileType'  : self.internalFileType
        }

class Party(object):
    '''
    Contract party.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): party fields.
        Dictionary keys:
            'id' Readonly. Autogenerated ID.
            'userId'
            'externalId'
            'name'
            'address'
            'mobile'
            'email'
            'signers'  Readonly. People who are required to sign for this
                       contract party.
            'contacts' Readonly. Additional people connected to this party who
                       may be contacted regarding the contract.
            'functionalReference' Functional reference of the party, for example
                                  Licensee, Provider, Lender, Seller.
            'terminationMode' One of : AFTER_ALL_SIGNERS_TERMINATE, AFTER_SINGLE_SIGNER_TERMINATES
        '''
        self.id = data.pop('id', None)
        self.userId = data.pop('userId', None)
        self.externalId = data.pop('externalId', None)
        self.name = data.pop('name', None)
        self.address = data.pop('address', None)
        self.mobile = data.pop('mobile', None)
        self.email = data.pop('email', None)
        self.functionalReference = data.pop('functionalReference', None)
        self.terminationMode = data.pop('terminationMode', None)

        self.signers = []
        for s in data.pop('signers', []):
            self.signers.append(Signer(s))

        self.contacts = []
        for c in data.pop('contacts', []):
            self.contacts.append(PartyContact(c))

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        signers = []
        for s in self.signers:
            signers.append(s.serialize())

        contacts = []
        for c in self.contacts:
            contacts.append(c.serialize())

        return {
            'id'                    : self.id,
            'userId'                : self.userId,
            'externalId'            : self.externalId,
            'name'                  : self.name,
            'address'               : self.address,
            'mobile'                : self.mobile,
            'email'                 : self.email,
            'contacts'              : contacts,
            'signers'               : signers,
            'functionalReference'   : self.functionalReference,
            'terminationMode'       : self.terminationMode
        }

class Signer(object):
    '''
    Party's signer.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): party fields.
        Dictionary keys:
            'id' Readonly. Autogenerated ID.
            'userId'
            'externalId'
            'name'
            'address'
            'mobile'
            'email'
            'signature'
            'termination'
        '''
        self.id = data.pop('id', None)
        self.userId = data.pop('userId', None)
        self.externalId = data.pop('externalId', None)
        self.name = data.pop('name', None)
        self.address = data.pop('address', None)
        self.mobile = data.pop('mobile', None)
        self.email = data.pop('email', None)
        self.signature = data.pop('signature', None)
        self.termination = data.pop('termination', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'id'                    : self.id,
            'userId'                : self.userId,
            'externalId'            : self.externalId,
            'name'                  : self.name,
            'address'               : self.address,
            'mobile'                : self.mobile,
            'email'                 : self.email,
            'signature'             : self.signature,
            'termination'           : self.termination
        }

class PartyContact(object):
    '''
    Party's contact.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): party fields.
        Dictionary keys:
            'id' Readonly. Autogenerated ID.
            'userId'
            'externalId'
            'name'
            'address'
            'mobile'
            'email'
            'role' One of the: CONTACT, BILLING, SUPPORT, ESCALATION, MANAGER,
                   BUSINESS, CONTRACT, TERMINATOR
        '''
        self.id = data.pop('id', None)
        self.userId = data.pop('userId', None)
        self.externalId = data.pop('externalId', None)
        self.name = data.pop('name', None)
        self.address = data.pop('address', None)
        self.mobile = data.pop('mobile', None)
        self.email = data.pop('email', None)
        self.role = data.pop('role', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'id'                    : self.id,
            'userId'                : self.userId,
            'externalId'            : self.externalId,
            'name'                  : self.name,
            'address'               : self.address,
            'mobile'                : self.mobile,
            'email'                 : self.email,
            'role'                  : self.role
        }
