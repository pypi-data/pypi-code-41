#!/usr/bin/env python
# coding: utf-8

from trivoreid.exceptions import TrivoreIDSDKException

class Invite(object):
    '''
    The class for constructing an invite request.
    '''

    def __init__(self,
                 emails,
                 nsCode,
                 groups,
                 subject=None,
                 body_text=None,
                 locale='fi'):
        '''
        Args:
            emails (str or list) : One or multiple emails to send the
                                   invitation.
            nsCode (str)         : Namespace code
            groups (str or list) : One or two of the group names or ids. It is
                                   not allowed to assign the Supervisor role
                                   through the invitation request.
            subject (str)        : Subject of the e-mail. If None, the default
                                   email will be sent.
            body_text (str)      : Body text of the e-mail. If None, the default
                                   email will be sent.
            locale (str)         : The language of the default e-mail. Should
                                   be fi, sv or en.
        '''

        if type(emails) is str:
            emails = [emails]

        if type(groups) is str:
            groups = [groups]

        self.request_body = {
                'emails' : emails,
                'nsCode' : nsCode,
                'groups' : groups,
                'locale' : locale
            }

        if subject is not None:
            self.request_body['subject'] = subject

        if body_text is not None:
            self.request_body['bodyText'] = body_text
