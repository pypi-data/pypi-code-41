#!/usr/bin/env python
# coding: utf-8

class SMSMessage(object):
    '''
    Object to wrap parameters for the SMS message.
    '''
    def __init__(self, data={}):
        '''
        Set parameters for the SMS message.
        Args:
            data (dict) : SMS parameters
        Dictionary fields:
            'to'            : Message recipient mobile phone number. Must be
                              valid phone number.
            'to-name'       : Message recipient display name. Used mostly for
                              user-interface purposes.
            'to-region'     : Message recipient default region (country or
                              subdivision). This affects number parsing only if
                              number is given in national format If this parameter
                              is missing, namespace's default region is used.
            'from'          : Message sender number or alphanumeric name. Maximum
                              length is 11 characters.
            'from-required' : Set message sender either required or optional. If
                              message sender (from) is set but this parameter is
                              false, message may be sent via gateway that does not
                              support sender address.
            'messageClass'  : Message class, one of 0,1,2,3
            'text'          : SMS message textual content.
            'data'          : SMS message binary content. Must be hex-encoded
            'udh'           : SMS message user data header. Must be hex-encoded
            'ttl'           : SMS time to live (validity) in minutes.
            'client-ref'    : Free-form, unique client reference for this message.
            'billing-ref'   : Free-form billing reference for this message.
            'carrier-ref'   : Free-form carrier reference for this message.
            'callback'      : Delivery report callback URL.
        '''
        self.to = data.pop('to', None)
        self.toName = data.pop('toName', None)
        self.toRegion = data.pop('toRegion', None)
        self.fromName = data.pop('from', None)
        self.fromRequired = data.pop('fromRequired', None)
        self.messageClass = data.pop('messageClass', None)
        self.text = data.pop('text', None)
        self.data = data.pop('data', None)
        self.udh = data.pop('udh', None)
        self.ttl = data.pop('ttl', None)
        self.clientRef = data.pop('carrierRef', None)
        self.billingRef = data.pop('billingRef', None)
        self.carrierRef = data.pop('carrierRef', None)
        self.callback = data.pop('callback', None)

    def serialize(self):
        '''
        Make object JSON serializable.
        '''
        return {
            'to'            : self.to,
            'toName'        : self.toName,
            'toRegion'      : self.toRegion,
            'from'          : self.fromName,
            'fromRequired'  : self.fromRequired,
            'messageClass'  : self.messageClass,
            'text'          : self.text,
            'data'          : self.data,
            'udh'           : self.udh,
            'ttl'           : self.ttl,
            'clientRef'     : self.clientRef,
            'billingRef'    : self.billingRef,
            'carrierRef'    : self.carrierRef,
            'callback'      : self.callback
        }

class SMSResponse(object):
    '''
    Class to wrap SMS response body.
    '''
    def __init__(self, data):
        self.response = {
            'status'            : data.pop('status', None),
            'description'       : data.pop('description', None),
            'action'            : data.pop('action', None),
            'messageId'         : data.pop('messageId', None),
            'to'                : data.pop('to', None),
            'toRegion'          : data.pop('toRegion', None),
            'clientRef'         : data.pop('clientRef', None),
            'billingRef'        : data.pop('billingRef', None),
            'carrierRef'        : data.pop('carrierRef', None),
            'messageCount'      : data.pop('messageCount', None),
            'billingState'      : data.pop('billingState', None),
            'totalPrice'        : data.pop('totalPrice', None),
            'remainingCredits'  : data.pop('remainingCredits', None)
        }
