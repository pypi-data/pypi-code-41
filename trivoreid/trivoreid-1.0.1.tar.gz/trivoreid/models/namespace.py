#!/usr/bin/env python
# coding: utf-8

from trivoreid.models.misc import Meta

class Namespace(object):
    '''
    Class that represents a namespace object.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): namespace fields
        Dictionary keys:
            'id' (str) - namespace ID
            'code' (str)
            'name' (str)
            'shortName' (str)
            'usernamePolicy' (UsernamePolicy) - if None, EIGHT_NUMBERS by defalt
            'commMethodMaxQty' Maximum number of email addresses and mobile
                               phone numbers allowed for users
            'duplicateNicknamesAllowed' Sets whether duplicate nicknames are
                                        allowed within the namespace
            'validFrom'
            'validTo'
            'smsSettings'
            'defaultGroupPolicy'
            'authorisationRestrictedMode' Restricted mode for the authoristions
                                          enabled. Can only be enabled in the
                                          Web UI.
            'meta' (dict) meta data
        '''

        self.id = data.pop('id', None)
        self.code = data.pop('code', None)
        self.name = data.pop('name', None)
        self.shortName = data.pop('shortName', None)
        self.usernamePolicy = data.pop('usernamePolicy', UsernamePolicy.EIGHT_NUMBERS)
        self.commMethodMaxQty = data.pop('commMethodMaxQty', 2)
        self.duplicateNicknamesAllowed = data.pop('duplicateNicknamesAllowed', False)
        self.validFrom = data.pop('validFrom', None)
        self.validTo = data.pop('validTo', None)
        self.smsSettings = SMSSettings(data.pop('smsSettings', {}))
        self.defaultGroupPolicy = DefaultGroupPolicy(data.pop('defaultGroupPolicy', {}))
        self.authorisationRestrictedMode = data.pop('authorisationRestrictedMode', None)
        self.meta = Meta(data.pop('meta', {}))

    def serialize(self, creating=False):
        '''
        Return JSON serializable dictionary with namespace fields.
        Args:
            creating If the new namespace is created. Default is False.
        '''

        namespace = {
            'id'                            : self.id,
            'code'                          : self.code,
            'name'                          : self.name,
            'shortName'                     : self.shortName,
            'usernamePolicy'                : self.usernamePolicy,
            'commMethodMaxQty'              : self.commMethodMaxQty,
            'duplicateNicknamesAllowed'     : self.duplicateNicknamesAllowed,
            'validFrom'                     : self.validFrom,
            'validTo'                       : self.validTo,
            'smsSettings'                   : self.smsSettings.serialize(),
            'authorisationRestrictedMode'   : self.authorisationRestrictedMode,
            'meta'                          : self.meta.serialize()
        }

        if not creating:
            namespace['defaultGroupPolicy'] = self.defaultGroupPolicy.serialize()

        return namespace

class UsernamePolicy:
    '''
    Namespace's username policies.
    '''
    EMAIL = 'EMAIL'
    FMLNN = 'FMLNN'
    CVCV = 'CVCV'
    CVCVCV = 'CVCVCV'
    EIGHT_NUMBERS = 'EIGHT_NUMBERS'
    NINE_NUMBERS = 'NINE_NUMBERS'
    TEN_NUMBERS = 'TEN_NUMBERS'
    EIGHT_LOWER_CASE_CHARS = 'EIGHT_LOWER_CASE_CHARS'
    TEN_LOWER_CASE_CHARS = 'TEN_LOWER_CASE_CHARS'
    MANUAL = 'MANUAL'

class SMSSettings(object):
    '''
    Class representing SMS settings for the namespace.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): SMS setting fields
        Dictionary keys:
            'enabled' (boolean) - SMS sending enables for the namespace
            'customEnabled' (boolean) Custom SMS sending enabled for the
                                      namespace. Custom SMS messages may be sent
                                      via the REST API or the Web UI.
            'defaultOriginator' (str) Alphanumeric Default originator for the
                                      SMS messages
            'defaultRegion' (str) Default region for parsing and validation.
                                  Represented by a two letter country code,
                                  eg. FI.
        '''

        self.enabled = data.pop('enabled', False)
        self.customEnabled = data.pop('customEnabled', False)
        self.defaultOriginator = data.pop('defaultOriginator', None)
        self.defaultRegion = data.pop('defaultRegion', None)

    def serialize(self):
        return {
            'enabled'           : self.enabled,
            'customEnabled'     : self.customEnabled,
            'defaultOriginator' : self.defaultOriginator,
            'defaultRegion'     : self.defaultRegion
        }

class DefaultGroupPolicy(object):
    '''
    Default group policy of the namespace. Sets many of the user settings.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): SMS setting fields
        Dictionary keys:
            'policyName' (str)
            'policyDescription' (str)
            'inactivityTime' (int)
            'resetPasswordOptions' (dict)
            'preferredLocale' (str)
            'preferredTimeFormat' (str) see PreferredTimeFormat
            'preferredDateFormat' (str) see PreferredDateFormat
            'displayNameFormat' (str) see DisplayNameFormat
            'timeZone' (str)
            'minPwLength' (int)
            'minCharClasses' (int)
            'pwMaxAge' (int)
            'pwHistorySaved' (int)
            'incorrectLoginAttemptsThresh' (int)
            'incorrectLoginTimeWin' (int)
            'incorrectLoginLockoutTime' (int)
            'maxPwSequenceLength' (int)
            'maxConsecutiveIdenticalChars' (int)
            'dataStoreCountry' (str)
            'passwordUserNameRuleEnforced' (boolean)
            'passwordDictionaryRuleEnforced' (boolean)
            'ciscoGroupPolicy' (str)
            'twoFactorAuthOptions' (str) see TwoFactorAuthOptions
            'loginAllowedIpRules' (list)
            'emailVerifyLinkExpireDays' (int)
            'mobileVerificationRequired' (boolean)
            'persistentLoginAllowed' (boolean)
            'emailLoginAllowed' (str) see IsAllowed
            'mobileLoginAllowed' (str) see IsAllowed
            'mobileVerificationAttemptsPerDay' (int)
            'strongIdRequiredForMyDataDownload' (boolean)
            'emailVerificationUnlocksUser' (boolean)
            'userImageAllowed' (boolean)
            'deleteMode' (str) see DeleteMode
            'hideOnSoftDelete' (boolean)
            'loginTargetBlacklist' (list)
        '''

        loginAllowedIpRules = []
        for l in data.pop('loginAllowedIpRules', []):
            loginAllowedIpRules.append(LoginAllowedIpRule(l))

        self.policyName = data.pop('policyName', None)
        self.policyDescription = data.pop('policyDescription', None)
        self.inactivityTime = data.pop('inactivityTime', None)
        self.resetPasswordOptions = ResetPasswordOptions(data.pop('resetPasswordOptions', {}))
        self.preferredLocale = data.pop('preferredLocale', None)
        self.preferredTimeFormat = data.pop('preferredTimeFormat', None)
        self.preferredDateFormat = data.pop('preferredDateFormat', None)
        self.displayNameFormat = data.pop('displayNameFormat', None)
        self.timeZone = data.pop('timeZone', None)
        self.minPwLength = data.pop('minPwLength', None)
        self.minCharClasses = data.pop('minCharClasses', None)
        self.pwMaxAge = data.pop('pwMaxAge', None)
        self.pwHistorySaved = data.pop('pwHistorySaved', None)
        self.incorrectLoginAttemptsThresh = data.pop('incorrectLoginAttemptsThresh', None)
        self.incorrectLoginTimeWin = data.pop('incorrectLoginTimeWin', None)
        self.incorrectLoginLockoutTime = data.pop('incorrectLoginLockoutTime', None)
        self.maxPwSequenceLength = data.pop('maxPwSequenceLength', None)
        self.maxConsecutiveIdenticalChars = data.pop('maxConsecutiveIdenticalChars', None)
        self.dataStoreCountry = data.pop('dataStoreCountry', None)
        self.passwordUserNameRuleEnforced = data.pop('passwordUserNameRuleEnforced', None)
        self.passwordDictionaryRuleEnforced = data.pop('passwordDictionaryRuleEnforced', None)
        self.ciscoGroupPolicy = data.pop('ciscoGroupPolicy', None)
        self.twoFactorAuthOptions = data.pop('twoFactorAuthOptions', None)
        self.loginAllowedIpRules = loginAllowedIpRules
        self.emailVerifyLinkExpireDays = data.pop('emailVerifyLinkExpireDays', None)
        self.mobileVerificationRequired = data.pop('mobileVerificationRequired', None)
        self.persistentLoginAllowed = data.pop('persistentLoginAllowed', None)
        self.emailLoginAllowed = data.pop('emailLoginAllowed', None)
        self.mobileLoginAllowed = data.pop('mobileLoginAllowed', None)
        self.mobileVerificationAttemptsPerDay = data.pop('mobileVerificationAttemptsPerDay', None)
        self.strongIdRequiredForMyDataDownload = data.pop('strongIdRequiredForMyDataDownload', None)
        self.emailVerificationUnlocksUser = data.pop('emailVerificationUnlocksUser', None)
        self.userImageAllowed = data.pop('userImageAllowed', None)
        self.deleteMode = data.pop('deleteMode', None)
        self.hideOnSoftDelete = data.pop('hideOnSoftDelete', None)
        self.loginTargetBlacklist = data.pop('loginTargetBlacklist', None)

    def serialize(self):

        loginAllowedIpRules = []
        for l in self.loginAllowedIpRules:
            loginAllowedIpRules.append(l.serialize())

        return {
            'policyName'                        : self.policyName,
            'policyDescription'                 : self.policyDescription,
            'inactivityTime'                    : self.inactivityTime,
            'resetPasswordOptions'              : self.resetPasswordOptions.serialize(),
            'preferredLocale'                   : self.preferredLocale,
            'preferredTimeFormat'               : self.preferredTimeFormat,
            'preferredDateFormat'               : self.preferredDateFormat,
            'displayNameFormat'                 : self.displayNameFormat,
            'timeZone'                          : self.timeZone,
            'minPwLength'                       : self.minPwLength,
            'minCharClasses'                    : self.minCharClasses,
            'pwMaxAge'                          : self.pwMaxAge,
            'pwHistorySaved'                    : self.pwHistorySaved,
            'incorrectLoginAttemptsThresh'      : self.incorrectLoginAttemptsThresh,
            'incorrectLoginTimeWin'             : self.incorrectLoginTimeWin,
            'incorrectLoginLockoutTime'         : self.incorrectLoginLockoutTime,
            'maxPwSequenceLength'               : self.maxPwSequenceLength,
            'maxConsecutiveIdenticalChars'      : self.maxConsecutiveIdenticalChars,
            'dataStoreCountry'                  : self.dataStoreCountry,
            'passwordUserNameRuleEnforced'      : self.passwordUserNameRuleEnforced,
            'passwordDictionaryRuleEnforced'    : self.passwordDictionaryRuleEnforced,
            'ciscoGroupPolicy'                  : self.ciscoGroupPolicy,
            'twoFactorAuthOptions'              : self.twoFactorAuthOptions,
            'loginAllowedIpRules'               : loginAllowedIpRules,
            'emailVerifyLinkExpireDays'         : self.emailVerifyLinkExpireDays,
            'mobileVerificationRequired'        : self.mobileVerificationRequired,
            'persistentLoginAllowed'            : self.persistentLoginAllowed,
            'emailLoginAllowed'                 : self.emailLoginAllowed,
            'mobileLoginAllowed'                : self.mobileLoginAllowed,
            'mobileVerificationAttemptsPerDay'  : self.mobileVerificationAttemptsPerDay,
            'strongIdRequiredForMyDataDownload' : self.strongIdRequiredForMyDataDownload,
            'emailVerificationUnlocksUser'      : self.emailVerificationUnlocksUser,
            'userImageAllowed'                  : self.userImageAllowed,
            'deleteMode'                        : self.deleteMode,
            'hideOnSoftDelete'                  : self.hideOnSoftDelete,
            'loginTargetBlacklist'              : self.loginTargetBlacklist
        }

class ResetPasswordOptions(object):
    '''
    Reset password options for the namespace.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): SMS setting fields
        Dictionary keys:
            'namespaceInfoHidden' (boolean)
            'namespaceInfoHiddenEnabled' (boolean)
            'allFieldsEnabled' (boolean)
        '''
        self.namespaceInfoHidden = data.pop('namespaceInfoHidden', None)
        self.namespaceInfoHiddenEnabled = data.pop('namespaceInfoHiddenEnabled', None)
        self.allFieldsEnabled = data.pop('allFieldsEnabled', None)

    def serialize(self):
        return {
            'namespaceInfoHidden': self.namespaceInfoHidden,
            'namespaceInfoHiddenEnabled': self.namespaceInfoHiddenEnabled,
            'allFieldsEnabled': self.allFieldsEnabled
        }

class LoginAllowedIpRule(object):
    '''
    Login Allowed Ip Rule of the namespace.
    '''

    def __init__(self, data={}):
        '''
        Args:
            data (dict): SMS setting fields
        Dictionary keys:
            'cidr' (str)
            'allowed' (boolean)
        '''
        self.cidr = data.pop('cidr', None)
        self.allowed = data.pop('allowed', None)

    def serialize(self):
        return {
            'cidr': self.cidr,
            'allowed': self.allowed
        }

class PreferredTimeFormat:
    '''
    Preferred time format.
    INHERIT, BROWSER, H_MM_SS_COLON_SEPARATOR
    '''
    INHERIT = 'INHERIT'
    BROWSER = 'BROWSER'
    H_MM_SS_COLON_SEPARATOR = 'H_MM_SS_COLON_SEPARATOR'

class PreferredDateFormat:
    '''
    Preferred date format.
    INHERIT, BROWSER, YYYY_MM_DD, D_M_YYYY, D_MON_YYYY
    '''
    INHERIT = 'INHERIT'
    BROWSER = 'BROWSER'
    H_MM_SS_COLON_SEPARATOR = 'YYYY_MM_DD'
    D_M_YYYY = 'D_M_YYYY'
    D_MON_YYYY = 'D_MON_YYYY'

class DisplayNameFormat:
    '''
    Preferred date format.
    Possible values:
        FIRSTNAME_MIDDLENAME_LASTNAME,
        FIRSTNAME_MIDDLENAME_INITIAL_LASTNAME,
        FIRSTNAME_LASTNAME,
        FIRSTNAME_MIDDLENAME_CAPITAL_LASTNAME,
        FIRSTNAME_MIDDLENAME_INITIAL_CAPITAL_LASTNAME,
        FIRSTNAME_CAPITAL_LASTNAME,
        LASTNAME_COMMA_FIRSTNAME_MIDDLENAME,
        LASTNAME_FIRSTNAME_MIDDLENAME,
        LASTNAME_COMMA_FIRSTNAME_MIDDLENAME_INITIAL,
        LASTNAME_FIRSTNAME_MIDDLENAME_INITIAL,
        LASTNAME_COMMA_FIRSTNAME,
        LASTNAME_FIRSTNAME,
        CAPITAL_LASTNAME_COMMA_FIRSTNAME_MIDDLENAME,
        CAPITAL_LASTNAME_FIRSTNAME_MIDDLENAME,
        CAPITAL_LASTNAME_COMMA_FIRSTNAME_MIDDLENAME_INITIAL,
        CAPITAL_LASTNAME_FIRSTNAME_MIDDLENAME_INITIAL,
        CAPITAL_LASTNAME_COMMA_FIRSTNAME,
        CAPITAL_LASTNAME_FIRSTNAME
    '''
    FIRSTNAME_MIDDLENAME_LASTNAME = 'FIRSTNAME_MIDDLENAME_LASTNAME'
    FIRSTNAME_MIDDLENAME_INITIAL_LASTNAME = 'FIRSTNAME_MIDDLENAME_INITIAL_LASTNAME'
    FIRSTNAME_LASTNAME = 'FIRSTNAME_LASTNAME'
    FIRSTNAME_MIDDLENAME_CAPITAL_LASTNAME = 'FIRSTNAME_MIDDLENAME_CAPITAL_LASTNAME'
    FIRSTNAME_MIDDLENAME_INITIAL_CAPITAL_LASTNAME = 'FIRSTNAME_MIDDLENAME_INITIAL_CAPITAL_LASTNAME'
    FIRSTNAME_CAPITAL_LASTNAME = 'FIRSTNAME_CAPITAL_LASTNAME'
    LASTNAME_COMMA_FIRSTNAME_MIDDLENAME = 'LASTNAME_COMMA_FIRSTNAME_MIDDLENAME'
    LASTNAME_FIRSTNAME_MIDDLENAME = 'LASTNAME_FIRSTNAME_MIDDLENAME'
    LASTNAME_COMMA_FIRSTNAME_MIDDLENAME_INITIAL = 'LASTNAME_COMMA_FIRSTNAME_MIDDLENAME_INITIAL'
    LASTNAME_FIRSTNAME_MIDDLENAME_INITIAL = 'LASTNAME_FIRSTNAME_MIDDLENAME_INITIAL'
    LASTNAME_COMMA_FIRSTNAME = 'LASTNAME_COMMA_FIRSTNAME'
    LASTNAME_FIRSTNAME = 'LASTNAME_FIRSTNAME'
    CAPITAL_LASTNAME_COMMA_FIRSTNAME_MIDDLENAME = 'CAPITAL_LASTNAME_COMMA_FIRSTNAME_MIDDLENAME'
    CAPITAL_LASTNAME_FIRSTNAME_MIDDLENAME = 'CAPITAL_LASTNAME_FIRSTNAME_MIDDLENAME'
    CAPITAL_LASTNAME_COMMA_FIRSTNAME_MIDDLENAME_INITIAL = 'CAPITAL_LASTNAME_COMMA_FIRSTNAME_MIDDLENAME_INITIAL'
    CAPITAL_LASTNAME_FIRSTNAME_MIDDLENAME_INITIAL = 'CAPITAL_LASTNAME_FIRSTNAME_MIDDLENAME_INITIAL'
    CAPITAL_LASTNAME_COMMA_FIRSTNAME = 'CAPITAL_LASTNAME_COMMA_FIRSTNAME'
    CAPITAL_LASTNAME_FIRSTNAME = 'CAPITAL_LASTNAME_FIRSTNAME'

class TwoFactorAuthOptions:
    '''
    Two Factor Authentication Options.
    Values:
        Allow TOTP and SMS OTP 2FA
        Allow TOTP 2FA only
        Request TOPT or SMS OTL 2FA
        Request TOTP 2FA
    '''
    ALLOW_TOTP_AND_SMS_OTL_2FA = 'Allow TOTP and SMS OTP 2FA'
    ALLOW_TOTP_2FA_ONLY = 'Allow TOTP 2FA only'
    REQUEST_TOTP_OR_SMS_OTL_2FA = 'Request TOPT or SMS OTL 2FA'
    REQUEST_TOTP_2FA = 'Request TOTP 2FA'

class IsAllowed:
    '''
    ALLOWED or DISALLOWED.
    '''
    ALLOWED = 'ALLOWED'
    DISALLOWED = 'DISALLOWED'

class DeleteMode:
    '''
    HARD_DELETE or SOFT_DELETE.
    '''
    HARD_DELETE = 'HARD_DELETE'
    SOFT_DELETE = 'SOFT_DELETE'
