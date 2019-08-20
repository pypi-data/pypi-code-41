'''
A-Shell orm fields

History:
    08-07-2019 - 1.0.0 - Stephen Funkhouser
        - Created
'''
from django.utils.translation import ugettext_lazy as _
from django.db import models


class PositiveBigIntegerField(models.BigIntegerField):
    empty_strings_allowed = False
    description = _('Big (8 byte) positive integer')

    def db_type(self, connection):
        '''
        Returns MySQL-specific column data type. Make additional checks
        to support other backends.
        '''
        return 'bigint UNSIGNED'

    def formfield(self, **kwargs):
        defaults = {'min_value': 0,
                    'max_value': BigIntegerField.MAX_BIGINT * 2 - 1}
        defaults.update(kwargs)
        return super(PositiveBigIntegerField, self).formfield(**defaults)


class AshBinary1(models.PositiveSmallIntegerField):
    ''' equivalent to b1 '''
    empty_strings_allowed = False
    description = _('A-Shell B1')

    def get_internal_type(self):
        return 'AshBinary1'


class AshBinary2(models.PositiveSmallIntegerField):
    ''' equivalent to b2 '''
    empty_strings_allowed = False
    description = _('A-Shell b2')

    def get_internal_type(self):
        return 'AshBinary2'


class AshBinary3(models.PositiveIntegerField):
    ''' equivalent to b3 '''
    empty_strings_allowed = False
    description = _('A-Shell b3')

    def get_internal_type(self):
        return 'AshBinary3'


class AshBinary4(models.PositiveIntegerField):
    ''' equivalent to B4 '''
    empty_strings_allowed = False
    description = _('A-Shell B4')

    def get_internal_type(self):
        return 'AshBinary4'


class AshBinary6(PositiveBigIntegerField):
    ''' equivalent to B6

    actually stored as 8 byte unsigned integer
    '''
    empty_strings_allowed = False
    description = _('A-Shell b6')

    def get_internal_type(self):
        return 'AshBinary6'


class AshJulianDate(AshBinary3):
    ''' equivalent to b3 '''
    # empty_strings_allowed = False
    description = _('A-Shell Julian Date')

    def get_internal_type(self):
        return 'AshJulianDate'


class AshString(models.CharField):
    ''' equivalent to string '''
    # empty_strings_allowed = False
    description = _('A-Shell String')

    def get_internal_type(self):
        return 'AshString'


class AshRecordStatus(models.CharField):
    ''' equivalent to string '''
    # empty_strings_allowed = False
    description = _('A-Shell Record Status')

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        super(AshRecordStatus, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'AshRecordStatus'


'''
- The idea here is to create a single db column compositekey
  comprising all the column values.
- the column will be added to the DB table
- you set the values in the member columns and it'll
  combine them automatically
- A-Shell ORM code generation will use this to determine the primary
  keys to use (key_format, DEFSTRUCTS, etc.)
'''

# class AshCompositeKey(object):
#     ''' possible object used in correspondence to AshCompositeKeyField.
#       used only when using Django's ORM, not A-Shell code templating
#     '''
#     def __init__(self, members):
#         '''
#         members - list of columns, in order, comprising the primary key
#         '''
#         self.members = members

ASH_FORMAT_LZEROS = 0
ASH_FORMAT_SPACES = 1

DEFAULT_AUTO_LEAVE = 0
DEFAULT_AUTO_OVERRIDE = 1
DEFAULT_AUTO_NOSET = 2


class AshCompositeKeyField(models.CharField):
    ''' Django field to handle composite keys

    inheriting from CharField because ISAM indexes have to be string
    '''
    empty_strings_allowed = False
    description = _('composite key handler')

    def __init__(self, members, *args, **kwargs):
        '''
        params:
            members    - list of columns, in order, comprising the primary key
            callback   - ** not implemented ** model callback method to allow
                    access to the other model fields
        '''
        # TODO: determine max_length based on max_length of members
        # kwargs['max_length'] = 104
        self.members = members
        super(AshCompositeKeyField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(HandField, self).deconstruct()
        # del kwargs["max_length"]
        return name, path, args, kwargs

    def get_internal_type(self):
        ''' Returns the type of the value expected by the Database. '''
        return 'AshCompositeKeyField'


class AshCompositeKeyMemberField(models.CharField):
    ''' Django field to handle candidate keys

    inheriting from CharField because ISAM indexes have to be string
    '''

    def __init__(self, key_format=ASH_FORMAT_SPACES, auto_key=False, *args, **kwargs):
        '''
        params:
            key_format - determines how the value is formatted for ISAM key
            auto_key   - determines if the field member is treated as having an auto generated id
        '''
        self.key_format = key_format
        self.auto_key = auto_key
        super(AshCompositeKeyMemberField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        ''' Returns the type of the value expected by the Database. '''
        return 'AshCompositeKeyMemberField'


class AshCandidateKeyField(models.CharField):
    ''' Django field to handle candidate keys

    inheriting from CharField because ISAM indexes have to be string
    '''

    def __init__(self, key_format=ASH_FORMAT_SPACES, *args, **kwargs):
        '''
        params:
            key_format - determines how the value is formatted for ISAM key
        '''
        # kwargs['primary_key'] = True
        self.key_format = key_format
        super(AshCandidateKeyField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        ''' Returns the type of the value expected by the Database. '''
        return 'AshCandidateKeyField'
