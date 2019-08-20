'''
Base Node Types

'''
import logging

from quick_scheme.field import FieldValue

from ..base_node import SchemeBaseNode
from ..exceptions import QuickSchemeValidationException
from ..qs_yaml import UnsortableOrderedDict


LOG = logging.getLogger(__name__)


class SchemeNode(SchemeBaseNode):
    ''' Basic Node - a dictionary with defined Fields '''

    # List of fields
    FIELDS = []
    # Allow undefined fields. if false, throw exception on undefined field
    ALLOW_UNDEFINED = False
    # Use ordered Dict when returning values. If False, use standard dict
    MAP_CLASS = None

    PRESERVE_ORDER = False
    # If true, and briefset is set, and it is the only field, output using
    # brief format
    BRIEF_OUT = False

    def _initialize(self, *_args, **_kwargs):
        ''' Initialization hook for object - called before the data is set'''
        self._data = {}
        identity = None
        briefset = None
        required = []
        fields = {}
        for idx, field in enumerate(self.FIELDS):
            value = field.value(self)
            fields[field.name] = (idx, value)
            #self._data[field.name] = value
            if field.identity:
                if identity:
                    LOG.warning(
                        "Multiple Identity fields. Ignoring field %s as identity in %s",
                        field.name, self._name)
                else:
                    identity = value
            if field.brief:
                if briefset:
                    LOG.warning(
                        "Multiple QuickSet fields. Ignoring field %s as BriefSet in %s",
                        field.name, self._name)
                else:
                    briefset = value
            if field.required:
                required.append(field)

        self._int_set('identity', identity)
        self._int_set('required', required)
        self._int_set('fields', fields)
        self._int_set('briefset', briefset)

    @property
    def _briefset_field(self):
        ''' Get briefset field, if there is one '''
        return self._int_get('briefset', None)

    def get(self, key, default_value):
        ''' Pass through get for properties '''
        value = self._data.get(key, None)
        if value is None:
            return default_value
        if isinstance(value, FieldValue):
            return value.value
        return value

    def _brief_set(self, data):
        ''' Brief Set of data '''
        brief_set_field = self._briefset_field
        if brief_set_field is not None:
            # print("BRIEF:: Setting field: %s to %s(%s)" %
            #      (brief_set_field.name(), data, type(data)))
            brief_set_field.set(data)
        else:
            raise QuickSchemeValidationException(
                "Node %s is defined via brief syntax but briefset field is not found" % self._name)

    def _set_identity(self, identity):
        ''' Set identity '''
        super(SchemeNode, self)._set_identity(identity)
        id_field = self._int_get('identity', None)
        if id_field and identity is not None:
            id_field.set(identity)

    def _get_map_class_instance(self, *args, **kwargs):
        ''' Get instance of map class appropriate for this object'''

        map_class = self.MAP_CLASS
        if map_class is None:
            if self.PRESERVE_ORDER:
                map_class = UnsortableOrderedDict
            else:
                map_class = dict
        return map_class(*args, **kwargs)

    @property
    def _fields(self):
        ''' Get fields '''
        return self._int_get('fields', {})

    def _set_data(self, data):
        ''' Set data for this object '''
        extra_data = self._get_map_class_instance()

        fields = self._fields
        if isinstance(data, dict):
            for key, value in data.items():
                indexed_value_holder = fields.get(key, None)
                if indexed_value_holder is not None:
                    _, value_holder = indexed_value_holder
                    value_holder.set(value, parent=self, identity=key)
                else:
                    if self.ALLOW_UNDEFINED:
                        extra_data[key] = value
                    else:
                        raise QuickSchemeValidationException(
                            "Invalid field '%s' for '%s'" % (key, self._name))
        else:
            # print("Invalid data type: %s for %s (%s)" %
            #      (type(data), self.quick_scheme.path_str(), data))
            self._brief_set(data)
        self._data = extra_data

    def _get_by_id(self, id):
        ''' Return by id '''
        fields = self._fields
        indexed_value_holder = fields.get(id, None)
        if indexed_value_holder is not None:
            _, value_holder = indexed_value_holder
            return value_holder.value
        elif self.ALLOW_UNDEFINED:
            return self._data.get(id, None)
        return None

    def _get_data(self):
        ''' Get data  '''
        data = self._get_map_class_instance()
        fields = self._fields
        for name, (_idx, field) in fields.items():
            if field.is_set or field.field.always:
                data[name] = field.get_data()
        if self.ALLOW_UNDEFINED:
            for name, value in self._data.items():
                data[name] = value
        #print("Data: %s (%s)" % (data, type(data)))
        return data

    def _children(self):
        ''' Return a list of tuples of index key and value for all child nodes '''
        children = []
        for child_name, (child_idx, child) in self._fields.items():
            children.append((child_name, child))
        if self.ALLOW_UNDEFINED:
            for key, value in self._data.items():
                children.append((key, value))
        return children

    def _validate_node(self):
        ''' Validate node '''
        for field_name, (field_idx, field) in self._fields.items():
            if field is None:
                LOG.warning("Something is wrong. Field %s for %s is defined improperly",
                            field_name, self._path_str())
                return False
            if not field.is_valid:
                LOG.warning("Field %s(%s) in object %s is not valid (%s)",
                            field_name, field_idx, self._path_str(), field.get())
                return False
        return True

    def _validate_qs_child(self, child_idx, child):
        ''' Validate single child item if child is a QS Node '''
        if not child.is_qs_node:
            return False
        child_value = child.get()
        if isinstance(child_value, SchemeBaseNode):
            return child_value.quick_scheme.validate()
        LOG.debug("Child %s of %s is valid", child_idx, self._path_str())
        # Should we return True if not a proper value?
        return False

    def _validate_children(self):
        ''' Validate node's children '''
        for child_idx, child in self._children():
            if isinstance(child, FieldValue) and child.is_qs_node:
                if not self._validate_qs_child(child_idx, child):
                    LOG.warning(
                        "Child value for child %s of %s is not valid", child_idx, self._path_str())
                    return False
        return True
