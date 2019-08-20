'''
Base Node Types

'''
import logging


LOG = logging.getLogger(__name__)


class ProxyAccess(object):
    ''' Allows transparent proxy to internal attributes of an object '''

    def __init__(self, real, silent=True):
        ''' Init '''
        self._real = real
        self._silent = silent

    def __getattr__(self, name):
        ''' Get internal name of the real object '''
        if self._real is not None:
            try:
                return getattr(self._real, "_%s" % name)
            except AttributeError as _ex:
                pass
            if self._silent:
                return None
            clazz = self._real.__class__.__name__
            raise AttributeError(
                "Failed to find attribute '_%s' in %s" % (name, clazz))

        if not self._silent:
            raise AttributeError(
                "Failed to find attribute '_%s': No Object" % name)
        return None


class SchemeBaseNode(object):
    ''' Base Scheme Object Node'''

    def __init__(self, parent=None, identity=None, data=None, **kwargs):
        ''' Initialize '''
        self._internal = {}
        self._parent = parent
        self._initialize(**kwargs)
        self._data = None
        self.quick_scheme = ProxyAccess(self)
        self._set_identity(identity)
        self._set_data(data)
        self._is_valid = self._validate(True)

    def _root(self):
        ''' Get root node '''
        if self._parent:
            return self._parent.quick_scheme.root()
        return self

    def _path_str(self):
        ''' Path as a string '''
        return ".".join(self._path())

    def _path(self):
        '''get path to this node '''
        if self._parent:
            path = self._parent.quick_scheme.path()
        else:
            path = []

        identity = self._get_identity()
        path.append(str(identity if identity is not None else ''))
        return path

    def _get_by_id(self, id):
        ''' Return by id '''
        return None

    def _get_by_path(self, path):
        ''' Get By Path '''
        node = self
        if path.startswith('.'):
            node = self._root()
        parts = path.split(".", 1)
        node = node.quick_scheme.get_by_id(parts[0])
        if node is None:
            return None
        if len(parts) > 1:
            return node.quick_scheme.get_by_path(parts[1])
        return node

    def _int_get(self, key, default_value=None):
        ''' Get internal parameter '''
        return self._internal.get(key, default_value)

    def _int_set(self, key, value):
        ''' Set internal parameter '''
        self._internal[key] = value

    def _int_setdefault(self, key, value):
        ''' Set internal parameter '''
        self._internal.setdefault(key, value)

    def _create_child(self, child_type, identity, value):
        ''' Create a child based on type '''
        if issubclass(child_type, SchemeBaseNode):
            return child_type(self, identity=identity, data=value)
        child_value = child_type(value)
        # print("Creating simple child type value: %s (%s)from %s" %
        #      (child_value, dict(), value))
        return child_value

    @classmethod
    def _class_name(cls):
        ''' Return Class Name '''
        return cls.__name__

    @property
    def _name(self):
        ''' Property for class name '''
        return self._class_name()

    def __repr__(self, *_args, **_kwargs):
        return "{QuickScheme::%s::%s}" % (self._name, repr(self._data))

    # To Be Implemented By Child Classes:

    def _initialize(self, *args, **kwargs):
        ''' Initialization hook for object - called before the data is set'''

    def _set_data(self, data):
        ''' Set data for this object '''
        self._data = data

    def _set_identity(self, identity):
        ''' Set identity for this node '''
        self._int_set('id', identity)

    def _get_identity(self):
        ''' Set identity for this node '''
        return self._int_get('id', '.')

    def _get_data(self):
        ''' Get data  '''
        return self._data

    def _children(self):
        ''' Return a list of tuples of index key and value for all child nodes '''
        return []

    def _validate_node(self):
        ''' Validate node '''
        return True

    def _validate_children(self):
        ''' Validate node's children '''
        return True

    def _validate(self, children=True):
        ''' Validate this node and its children '''
        if children:
            return self._validate_node() and self._validate_children()
        return self._validate_node()
