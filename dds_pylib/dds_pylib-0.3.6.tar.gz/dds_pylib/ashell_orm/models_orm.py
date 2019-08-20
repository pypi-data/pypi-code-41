'''
A-Shell orm models

History:
    08-07-2019 - 1.0.0 - Stephen Funkhouser
        - Created
'''
from __future__ import unicode_literals
from exceptions import Exception

from django.db import models
from dds_pylib.pyext.struct import Struct


class AshNoKeyException(Exception):
    ''' exception '''

class AshFileStruct(Struct):
    ''' file structure '''
    record_size = 0 # not used yet
    fileio_define = ''  # defaults to the model name (i.e. FILEIO_ZONE)


class AshModel(models.Model):
    ''' add methods necessary for
    - composite key fields
    - ORM code generation
    '''

    def __init__(self, *args, **kwargs):
        super(AshModel, self).__init__(*args, **kwargs)

        # tells us whether or not to use '.key' by default in variable member name
        self.use_defstruct_key = True
        # primary_file = None
        self.primary_file = AshFileStruct()

        self.__has_key = None

    def fields_iter(self):
        ''' Django model field generator '''
        for f in self._meta.get_fields():
            yield f

    def get_field(self, field):
        for f in self.fields_iter():
            if f.name == field:
                return f

    @property
    def get_primary_fileio_define(self):
        fd = ''
        if self.primary_file is None:
            fd = 'FILEIO_%ORM_MODEL_UPPER%'
        elif not self.primary_file.fileio_define:
            fd = 'FILEIO_%ORM_MODEL_UPPER%'
        else:
            fd = self.primary_file.fileio_define
        return fd

    def is_field_key(self, field, inc_compsite_key=True):
        ''' determine if field is a key field

        params:
            inc_compsite_key - True include linking 'cmpkey'
                               False don't include
        '''
        if self.has_key():
            if self.has_candidate_key():
                if self.is_ash_candidate_key_field(field):
                    return True
            elif self.has_composite_key():
                if self.is_ash_composite_key_member_field(field):
                    return True
                if inc_compsite_key:
                    if self.is_ash_composite_key_field(field):
                        return True
        return False

    def is_ash_candidate_key_field(self, f):
        ''' determine if field is an ashell candidate key field
        params:
            f - django model field
        '''
        if f.get_internal_type() == 'AshCandidateKeyField':
            return True
        return False

    def is_ash_composite_key_field(self, f):
        ''' determine if field is an ashell composite key field
        params:
            f - django model field
        '''
        if f.get_internal_type() == 'AshCompositeKeyField':
            return True
        return False

    def is_ash_composite_key_member_field(self, f):
        ''' determine if field is an ashell composite key field
        params:
            f - django model field
        '''
        if f.get_internal_type() == 'AshCompositeKeyMemberField':
            return True
        return False

    def has_key(self):
        ''' determine if Model has a key defined, agnostic to type '''
        if self.__has_key is None:
            if self.has_candidate_key():
                self.__has_key = True
            elif self.has_composite_key():
                self.__has_key = True
            else:
                self.__has_key = False
        return self.__has_key

    def has_candidate_key(self):
        ''' determine if model has a candidate key defined. used by has_key '''
        if self.is_ash_candidate_key_field(self._meta.pk):
            return True
        return False

    def has_composite_key(self):
        ''' determine if model has a composite key defined. used by has_key '''
        if self.is_ash_composite_key_field(self._meta.pk):
            return True
        return False

    def get_key_field(self):
        ''' get model key field agnostic to type '''
        if self.has_key():
            return self._meta.pk

    def key_field_iter(self, inc_auto_key=True, only_auto_key=False):
        ''' iterator over key fields agnostic to composite/candidate keys
        params:
            inc_auto_key - False exclude auto_key=True keys
                           (currently only applies to composite)
            only_auto_key - True only include auto_key
                            (overrides inc_auto_key=False)
                            (currently only applies to composite)
            returns:
            django model field
        '''
        if self.has_key():
            if only_auto_key:
                inc_auto_key = True

            key_field = self.get_key_field()
            if self.has_candidate_key():
                yield self._meta.pk
            elif self.is_ash_composite_key_field(key_field):
                # if composite key iterate the members
                for member in key_field.members:
                    field = self.get_field(field=member)
                    if only_auto_key:
                        yield field
                    elif inc_auto_key:
                        yield field
                    elif not field.auto_key:
                        yield field
        else:
            raise AshNoKeyException('model has no key')

    def print_key_name(self):
        if self.has_key():
            key_field = self.get_key_field()
            print 'key_field: ', key_field
            for member in self.key_field_iter():
                print ('type: {t} member: {m}'.format(
                    t=type(member),
                    m=member.name
                ))
        else:
            print('no key')

    def print_fields(self, columns=True, keys=True):
        def ln(ct):
            print ('{c}'.format(c='-' * ct))

        ln(80)
        if columns:
            ct = 0
            for f in self._meta.get_fields():
                ct += 1
                print ('field: {f} {t1}'.format(
                    f=f,
                    t1=f.get_internal_type(),
                ))
        else:
            ct = len([_ for _ in self._meta.get_fields()])
        print ('table=[{tbl}] app=[{a}] ct=[{ct}]'.format(
            tbl=self._meta.db_table, a=self._meta.app_label, ct=ct))
        print ('pk_name=[{pkn}] pk_col=[{pkc}]'.format(
            pkn=self._meta.pk.name, pkc=self._meta.pk.column))

        if keys:
            print('hck: ', self.has_composite_key())
            self.print_key_name()

        ln(80)

    class Meta:
        abstract = True
