#!/usr/bin/env python
# coding: utf-8

class PasswordRequirements(object):
    '''
    The class that represents password requirements.
    '''

    def __init__(self, data = None):
        '''
        Args:
            data (dict) : password requirements
        Dictionary parameters:
            minLength (int) : minimum password length.
            maxLength (int) : maximum password length.
            numberOfCharacteristics (int)
            alphabeticalSequenceMaxLength (int)
            numericalSequenceMaxLength (int)
            qwertySequenceMaxLength (int)
            historyLength (int)
            repeatCharacterLength (int)
            usernameForbidden (bool)
            dictionaryCheck (bool)
        '''
        self.minLength = data.pop('minLength', None)
        self.maxLength = data.pop('maxLength', None)

        self.numberOfCharacteristics = data.pop('numberOfCharacteristics', None)
        self.alphabeticalSequenceMaxLength = data.pop(
                            'alphabeticalSequenceMaxLength', None)
        self.numericalSequenceMaxLength = data.pop(
                            'numericalSequenceMaxLength', None)
        self.qwertySequenceMaxLength = data.pop('qwertySequenceMaxLength', None)
        self.historyLength = data.pop('historyLength', None)
        self.repeatCharacterLength = data.pop('repeatCharacterLength', None)
        self.usernameForbidden = data.pop('usernameForbidden', None)
        self.dictionaryCheck = data.pop('dictionaryCheck', None)

    def serialize(self):
        return {
            'minLength' : self.minLength,
            'maxLength' : self.minLength,
            'numberOfCharacteristics' : self.numberOfCharacteristics,
            'alphabeticalSequenceMaxLength' : self.alphabeticalSequenceMaxLength,
            'numericalSequenceMaxLength' : self.numericalSequenceMaxLength,
            'qwertySequenceMaxLength' : self.qwertySequenceMaxLength,
            'historyLength' : self.historyLength,
            'repeatCharacterLength' : self.repeatCharacterLength,
            'usernameForbidden' : self.usernameForbidden,
            'dictionaryCheck' : self.dictionaryCheck
        }
