#!/usr/bin/env python
# coding: utf-8

from trivoreid.exceptions import TrivoreIDSDKException

class Email(object):
    '''
    Wrapper for the Email message.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict) : email fields
        Dictionary keys:
            'to'            : list of To addresses
            'cc'            : list of CC addresses
            'bcc'           : list of BCC addresses
            'from'          : from email address (string)
            'replyTo'       : list of Reply-To addresses
            'subject'       : email subject
            'html'          : HTML content of email
            'text'          : text content of email
            'attachments'   : attachments to email. In the response this
                              field is omitted.
        '''
        to = []
        for e in data.pop('to', []):
            to.append(EmailAddress(e))

        cc = []
        for e in data.pop('cc', []):
            cc.append(EmailAddress(e))

        bcc = []
        for e in data.pop('bcc', []):
            bcc.append(EmailAddress(e))

        replyTo = []
        for e in data.pop('replyTo', []):
            replyTo.append(EmailAddress(e))

        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.replyTo = replyTo
        self.from_email = data.pop('from', None)
        self.subject = data.pop('subject', None)
        self.html = data.pop('html', None)
        self.text = data.pop('text', None)
        self.attachments = EmailAttachments(data.pop('attachments', {}))

    def construct_email(self,
                        to=None,
                        cc=None,
                        bcc=None,
                        from_email=None,
                        reply_to=None,
                        subject=None,
                        html=None,
                        text=None,
                        attachments=None):
        '''
        Construct email fields.
        NB! Fields will be overwriten!
        Args:
            'to' (list)                 : list of To addresses
            'cc' (list)                 : list of CC addresses
            'bcc' (list)                : list of BCC addresses
            'from_email' (str, dict)    : a single from email address or a
                                          dictionary with email fields.
            'replyTo' (list)            : list of Reply-To addresses
            'subject' (str)             : email subject
            'html' (str)                : HTML content of email
            'text' (str)                : text content of email
            'attachments'               : attachments to email. In the response this
                                          field is omitted.
        '''
        to = self._check_addresses(to)
        cc = self._check_addresses(cc)
        bcc = self._check_addresses(bcc)
        reply_to = self._check_addresses(reply_to)

        if from_email is not None:
            if type(from_email) in [str, dict]:
                from_email = EmailAddress(from_email)
            elif 'EmailAddress' is not str(type(from_email)):
                raise TrivoreIDSDKException('Wrong type of the email!')

        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.replyTo = reply_to
        self.from_email = from_email
        self.subject = subject
        self.html = html
        self.text = text
        self.attachments = attachments

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        self._check_nulls()

        to = []
        for e in self.to:
            to.append(e.serialize())

        cc = []
        for e in self.cc:
            cc.append(e.serialize())

        bcc = []
        for e in self.bcc:
            bcc.append(e.serialize())

        replyTo = []
        for e in self.replyTo:
            replyTo.append(e.serialize())

        return {
            'to'            : to,
            'cc'            : cc,
            'bcc'           : bcc,
            'from'          : self.from_email.serialize(),
            'replyTo'       : replyTo,
            'subject'       : self.subject,
            'html'          : self.html,
            'text'          : self.text,
            'attachments'   : self.attachments.serialize()
        }

    def _check_addresses(self, data):
        '''
        Check single adddress.
        '''
        if (data == None):
            return []

        if type(data) == list:
            addresses = []
            for e in data:
                addresses.append(EmailAddress(e))
            return addresses
        elif type(data) == str:
            return [EmailAddress(data)]
        elif 'EmailAddress' in str(type(data)):
            return data
        else:
            raise TrivoreIDSDKException('Wrong type of the email!')

    def _check_nulls(self):
        if self.to is None:
            self.to = []
        if self.cc is None:
            self.cc = []
        if self.bcc is None:
            self.bcc = []
        if self.replyTo is None:
            self.replyTo = []
        if self.attachments is None:
            self.attachments = EmailAttachments()
        if self.from_email is None:
            self.from_email = EmailAddress()

class EmailAddress(object):
    '''
    Wrapper for a single email address.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict, str): email fields or a single email address
        Dictionary keys:
            'name'          : email address name
            'address'       : email address
            'verified'      : verification status
            'verifiedBy'    : verified by
            'tags'          : email address tags
        '''
        if type(data) is str:
            self.address = data
            self.name = None
            self.verified = None
            self.verifiedBy = None
            self.tags = None
        elif type(data) is dict:
            self.address = data.pop('address', None)
            self.name = data.pop('name', None)
            self.verified = data.pop('verified', False)
            self.verifiedBy = data.pop('verifiedBy', None)
            self.tags = data.pop('tags', None)
        else:
            raise TrivoreIDSDKException('Wrong type of the email!')

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return {
            'name'          : self.name,
            'address'       : self.address,
            'verified'      : self.verified,
            'verifiedBy'    : self.verifiedBy,
            'tags'          : self.tags
        }

class EmailAttachments(object):
    '''
    Wrapper for the email attachments.
    '''
    def __init__(self, data={}):
        '''
        Args:
            data (dict): attachment fields
        Dictionary keys:
            'name' : attachment file name
            'data' : attachment data, base64 encoded
        '''
        self.attachments = []
        if type(data) is dict and bool(data):
            data = [data]

        for i in range(len(data)):
            self.attachments.append({'name': data[i].pop('name', None),
                                     'data': data[i].pop('data', None)})

    def add_attachment(self, name, data):
        '''
        Args:
            'name' : attachment file name
            'data' : attachment data, base64 encoded
        '''
        self.attachments.append({'name' : name, 'data' : data})

    def serialize(self):
        '''
        Return dictionary that is JSON serializable.
        '''
        return self.attachments
