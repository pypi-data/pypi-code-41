from types import FunctionType
from base_aios.validate.lang import lang
import re

HTTP_RE = re.compile(r'^((https|http|ftp|rtsp|mms)?:\/\/)[^\s]+')
TEL_RE = re.compile(r'^0?(13|14|15|17|18|19)[0-9]{9}$')
EMAIL_RE = re.compile(r'\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}')

class ParamsValid(object):

    def __init__(self, **args):
        self.v_map = {
            'type': self.validate_type,
            'required': self.validate_required,
            'minlen': self.validate_minlen,
            'maxlen': self.validate_maxlen,
            'max': self.validate_max,
            'min': self.validate_min,
            're': self.validate_re,
            'function': self.validate_function,
            'enum': self.validate_enum
        }
        self.fields = args or {}

    def validate(self, data={}):
        try:
            for field in self.fields:
                rules = self.fields.get(field)
                rules.setdefault('type', str)

                v_data = data.get(field)

                required = rules.get('required')
                if required is None and v_data is None:
                    continue
                for rule in rules:
                    v_rule = rules.get(rule)
                    fn = self.v_map.get(rule)
                    if fn:
                        is_valid, msg = fn(v_rule, field, v_data)
                        if not is_valid:
                            raise Exception('{} {}'.format(lang.resp('L_PARAMS_VERIFICATION_FAILED'), msg))
                    else:
                        raise Exception('{} [{}]'.format(lang.resp('L_UNKNOWN_VALIDATION_TYPE'), rule))
            return True, ''
        except Exception as err:
            return False, str(err)

    def validate_type(self, rule, key, value):
        if isinstance(value, rule):
            return True, ''
        else:
            try:
                rule(value)
                return True, ''
            except Exception as err:
                pass
            return False, '{}  {}'.format(lang.resp('L_DATA_TYPE_NOT_MATCH'), key)
                
    def validate_required(self, rule, key, value):
        if rule:
            if value is not None and value is not '':
                return True, ''
            else:
                return False, '{}  {}'.format(lang.resp('L_REQUIRED_ITEMS_CAN_NOT_BE_EMPTY'), key) 
        else:
            return True, ''

    def validate_minlen(self, rule, key, value):
        if rule <= len(value):
            return True, ''
        else:
            return False, '{}  {}'.format(lang.resp('L_LENGTH_OF_THE_STRING_EXCEEDS_THE_LIMIT'), key)

    def validate_maxlen(self, rule, key, value):
        if len(value) <= rule:
            return True, ''
        else:
            return False, '{}  {}'.format(lang.resp('L_LENGTH_OF_THE_STRING_EXCEEDS_THE_LIMIT'), key)

    def validate_min(self, rule, key, value):
        if rule <= float(value):
            return True, ''
        else:
            return False, '{}  {}'.format(lang.resp('L_VALUE_RANGE_EXCEEDS_THE_LIMIT'), key)

    def validate_max(self, rule, key, value):
        if float(value) <= rule:
            return True, ''
        else:
            return False, '{}  {}'.format(lang.resp('L_VALUE_RANGE_EXCEEDS_THE_LIMIT'), key)

    def validate_re(self, rule, key, value):
        if rule.match(value):
            return True, ''
        else:
            return False, '{}  {}'.format(lang.resp('L_DATA_FORMAT_ERROR'), key)

    def validate_function(self, rule, key, value):
        if isinstance(rule, FunctionType):
            if rule(value):
                return True, ''
        return False, '{}  {}'.format(lang.resp('L_CALLBACK_VALIDATE_ERROR'), key)

    def validate_enum(self, rule, key, value):
        if value in rule:
            return True, ''
        else:
            return False, '{}  {}'.format(lang.resp('L_ENUM_VALIDATE_ERROR'), key)
