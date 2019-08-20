''' Field Definitions '''
import logging
from .base_node import SchemeBaseNode


LOG = logging.getLogger(__name__)

STR = str

FIELD_DEFAULTS = dict(identity=False,
                      ftype=STR,
                      required=False,
                      default=None,
                      always=True,
                      brief=False,
                      validator=None)


class FieldValue(object):
    '''
    Field Value Holder

    This object holds a specific value for a specific node
    '''

    def __init__(self, field, node):
        '''
        Field value

        :param field: Field definition
        :param node: Node instance
        '''
        self.field = field
        self.value = None
        self.is_set = False
        self.node = node

    def name(self):
        ''' Get name for this field '''
        return self.field.name

    @property
    def is_qs_node(self):
        ''' Return true, if ftype is a QuickScheme node(derivative of SchemeBaseNode)'''
        return self.field.is_qs_node

    @property
    def is_required(self):
        ''' Check if this field is required '''
        return self.field.required

    def set(self, value, identity=None, parent=None):
        ''' Set value '''
        self.is_set = True
        if self.is_qs_node:
            self.value = self.field.ftype(
                parent=parent, identity=identity, data=value)
        else:
            self.value = self.field.ftype(value)

        return self

    def get_data(self):
        ''' Get value or default as pure data '''
        value = self.get()
        if isinstance(value, SchemeBaseNode):
            data = value.quick_scheme.get_data()
            #ident = value.quick_scheme.get_identity()
            # print("** Data for %s - %s is %s (%s)" %
            #      (ident if ident is not None else '*', self.name(), data, type(data)))

            return data
        # print("** Data value type is %s for %s (%s)" %
        #      (type(value), self.name(), self.field.ftype))
        return value

    def clear(self):
        ''' Clear value '''
        self.is_set = False
        self.value = None

    def get(self):
        ''' Get value or default, if not self '''
        return self.value if self.is_set else self.field.default

    @property
    def is_valid(self):
        ''' Check if this field value is valid '''
        if self.node:
            if self.field.required and not self.is_set:
                LOG.debug("Field '%s' in '%s' is required but not set",
                          self.name(), self.node._path_str())
                return False
            return self.field.validate(self)
        return True


class Field(object):
    ''' Basic Field '''

    # Python version independent version of a string
    STR = STR

    def __init__(self, name, **kwargs):
        '''
        Field Constructor

        :param name: Field Name (required)
        :param identity: if True, set this to be the identity field
        :param ftype: Field Type. Default is str
        :param required: If True
        :param default: default value if unset.
        :param always: If True(default) show when asking for data with default value, else hide
        :param brief: If True(default) this field is the brief-set field
        :param validator: If set to a callable, call to validate the field. The callable provided
          must take in FieldValue as positional parameter.
        '''
        self.name = name
        self._data = dict(FIELD_DEFAULTS)
        self._data.update(kwargs)

    def __getattr__(self, item):
        ''' Get attribute '''
        if item in self._data:
            return self._data.get(item, None)
        raise AttributeError("Invalid field attribute %s" % item)

    @property
    def is_qs_node(self):
        ''' 
        Returns true, if type for this field is a QuickScheme Node (i.e. a child of SchemeBaseNode)
         '''
        return issubclass(self.ftype, SchemeBaseNode)

    @property
    def has_default(self):
        ''' 
        Returns True if this field has a default value '''
        default = self._data.get('default', None)
        return default is not None

    @property
    def default(self):
        ''' Get default value '''
        default = self._data.get('default', None)
        ftype = self.ftype
        return default if default is not None else ftype()

    def value(self, node):
        ''' Create a FieldValue object '''
        return FieldValue(self, node)

    def validate(self, field_value):
        ''' Hook to Validate this field '''
        validator = self.validator
        if validator and callable(validator):
            return validator(field_value)
        return True
