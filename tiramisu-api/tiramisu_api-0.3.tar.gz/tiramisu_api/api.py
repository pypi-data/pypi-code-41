from typing import Optional, Dict, List, Any
from copy import copy
import warnings
import re


from .error import APIError, ConfigError, ValueWarning, ValueOptionError, ValueErrorWarning, PropertiesOptionError, display_list
from .setting import undefined
from .i18n import _


TIRAMISU_FORMAT = '1.0'
DEBUG = False


TYPE = {'boolean': bool,
        'integer': int,
        'string': str,
        'password': str,
        'filename': str,
        'email': str,
        'url': str,
        'ip': str,
        'network': str,
        'netmask': str,
        'broadcast_address': str,
        'port': str,
        'domainname': str,
        'date': str}


class Option:
    # fake Option (IntOption, StrOption, ...)
    # only usefull for warnings
    def __init__(self,
                 path,
                 display_name):
        self.path = path
        self.display_name = display_name

    def __call__(self):
        # suppose to be a weakref
        return self

    def impl_getpath(self):
        return self.path

    def impl_get_display_name(self):
        return self.display_name


class TiramisuOptionOption:
    # config.option(path).option

    def __call__(self,
                 path: str,
                 index: Optional[int]=None) -> 'TiramisuOption':
        # config.option(path).option(path)
        path = self._path + '.' + path
        schema = self.config.get_schema(path)
        if schema['type'] in ['object', 'array']:
            return TiramisuOptionDescription(self.config,
                                             schema,
                                             path)
        return TiramisuOption(self.config,
                              schema,
                              path,
                              index)
    def __init__(self,
                 config: 'Config',
                 path: str,
                 schema: Dict) -> None:
        self.config = config
        self._path = path
        self.schema = schema

    def doc(self):
        description = self.description()
        if not description:
            return self.name()
        return description

    def description(self):
        if self.issymlinkoption():
            schema = self.config.get_schema(self.schema['opt_path'])
        else:
            schema = self.schema
        return schema['title']

    def path(self):
        return self._path

    def name(self,
             follow_symlink: bool=False) -> str:
        if not follow_symlink or \
                self.isoptiondescription() or \
                not self.issymlinkoption():
            path = self._path
        else:
            path = self.schema['opt_path']
        return path.rsplit('.', 1)[-1]

    def isoptiondescription(self):
        return self.schema['type'] in ['object', 'array']

    def isleadership(self):
        return self.schema['type'] == 'array'

    def isleader(self):
        return self.config.isleader(self._path)

    def isfollower(self):
        return self.config.isfollower(self._path)

    def issymlinkoption(self) -> bool:
        return self.schema['type'] == 'symlink'

    def ismulti(self) -> bool:
        return self.schema.get('isMulti', False)

    def issubmulti(self) -> bool:
        return self.schema.get('isSubMulti', False)

    def type(self) -> str:
        if self.isleadership():
            return 'leadership'
        if self.isoptiondescription():
            return 'optiondescription'
        if self.issymlinkoption():
            return self.config.get_schema(self.schema['opt_path'])['type']
        return self.schema['type']

    def properties(self) -> List[str]:
        model = self.config.model.get(self._path, {})
        if self.isfollower():
            model = model.get('null', {})
        return self.config.get_properties(model, self._path, None)
#
#    def requires(self) -> None:
#        # FIXME
#        return None

    def pattern(self):
        if self._path in self.config.form:
            return self.config.form[self._path].get('pattern')
        else:
            return None

    def defaultmulti(self):
        if not self.schema.get('isMulti'):
            raise Exception('defaultmulti avalaible only for a multi')
        return self.schema.get('defaultmulti')


class TiramisuOptionProperty:
    # config.option(path).property
    def __init__(self,
                 config: 'Config',
                 path: str,
                 index: Optional[int]) -> None:
        self.config = config
        self.path = path
        self.index = index

    def get(self, only_raises=False):
        if not only_raises:
            model = self.config.model.get(self.path, {})
            props = self.config.get_properties(model, self.path, self.index, only_raises)
        else:
            props = []
        if self.config.is_hidden(self.path,
                                 self.index):
            props.append('hidden')
        return props


class _Value:
    def _dict_walk(self,
                   ret: Dict,
                   schema: Dict,
                   root: str,
                   fullpath: bool,
                   withwarning: bool,
                   flatten: bool,
                   len_parent: Optional[int]) -> None:
        leadership_len = None
        for key, option in schema['properties'].items():
            if self.config.is_hidden(key, None) is False:
                if flatten:
                    nkey = key.split('.')[-1]
                elif not fullpath and len_parent is not None:
                    nkey = key[len_parent:]
                else:
                    nkey = key
                if option['type'] in ['object', 'array']:
                    # optiondescription or leadership
                    self._dict_walk(ret,
                                    option,
                                    root,
                                    fullpath,
                                    withwarning,
                                    flatten,
                                    len_parent)
                elif schema.get('type') == 'array' and leadership_len is not None:
                    # followers
                    values = []
                    for index in range(leadership_len):
                        value = self.config.get_value(key,
                                                      index)
                        self.config._check_raises_warnings(key, index, value, option['type'], withwarning)
                        values.append(value)
                    ret[nkey] = values
                else:
                    value = self.config.get_value(key)
                    self.config._check_raises_warnings(key, None, value, option['type'], withwarning)
                    ret[nkey] = value
                    if schema.get('type') == 'array':
                        leadership_len = len(value)
            elif schema.get('type') == 'array' and leadership_len is None:
                # if leader is hidden, followers are hidden too
                break

    def dict(self,
             fullpath: bool=False,
             withwarning: bool=False,
             flatten: bool=False):
        ret = {}
        self._dict_walk(ret,
                        self.schema,
                        self.path,
                        fullpath,
                        withwarning,
                        flatten,
                        None)
        return ret


class TiramisuOptionOwner:
    # config.option(path).owner
    def __init__(self,
                 config: 'Config',
                 schema: Dict,
                 path: str,
                 index: int) -> None:
        self.config = config
        self.schema = schema
        self.path = path
        self.index = index

    def isdefault(self) -> Any:
        return self.config.get_owner(self.path, self.index) == 'default'

    def get(self) -> str:
        return self.config.get_owner(self.path, self.index)


class TiramisuOptionDescriptionValue(_Value):
    # config.option(descr_path).value
    def __init__(self,
                 config: 'Config',
                 schema: Dict,
                 path: str,
                 index: int) -> None:
        self.config = config
        self.schema = schema
        self.path = path
        self.index = index

    def dict(self,
             fullpath: bool=False,
             withwarning: bool=False,
             flatten: bool=False):
        ret = {}
        len_parent = len(self.path) + 1
        self._dict_walk(ret,
                        self.schema,
                        self.path,
                        fullpath,
                        withwarning,
                        flatten,
                        len_parent)
        return ret


class TiramisuOptionValue(_Value):
    # config.option(path).value
    def __init__(self,
                 config: 'Config',
                 schema: Dict,
                 path: str,
                 index: int) -> None:
        self.config = config
        self.schema = schema
        self.path = path
        self.index = index

    def get(self) -> Any:
        if self.schema['type'] == 'symlink':
            # FIXME should tested it too
            pass
        elif self.config.isfollower(self.path):
            if self.index is None:
                raise APIError(_('index must be set with the follower option "{}"').format(self.path))
        elif self.index is not None:
            raise APIError(_('index must only be set with a follower option, not for "{}"').format(self.path))
        if self.config.is_hidden(self.path, self.index):
            raise PropertiesOptionError(None, {'disabled'}, None, opt_type='option')
        value = self.config.get_value(self.path, self.index)
        self.config._check_raises_warnings(self.path, self.index, value, self.schema['type'])
        return value

    def list(self):
        return self.schema['enum']

    def _validate(self, type_, value):
        if value in [None, undefined]:
            return
        if type_ == 'symlink':
            raise ConfigError(_("can't assign to a SymLinkOption"))
        if type_ == 'choice':
            if 'enum' in self.schema and value not in self.schema['enum']:
                raise ValueError('value {} is not in {}'.format(value, self.schema['enum']))
        elif not isinstance(value, TYPE[type_]):
            raise ValueError('value {} is not a valid {} '.format(value, type_))

    def set(self, value):
        type_ = self.schema['type']
        leader_old_value = undefined
        if self.config.is_hidden(self.path, self.index):
            raise PropertiesOptionError(None, {'disabled'}, None, opt_type='option')
        if self.config.isleader(self.path):
            leader_old_value = self.config.get_value(self.path)
        remote = self.config.form.get(self.path, {}).get('remote', False)
        if self.index is None and self.schema.get('isMulti', False):
            if not isinstance(value, list):
                raise ValueError('value must be a list')
            for val in value:
                if self.schema.get('isSubMulti', False):
                    for v in val:
                        self._validate(type_, v)
                else:
                    self._validate(type_, val)
        else:
            if self.schema.get('isSubMulti', False):
                for val in value:
                    self._validate(type_, val)
            else:
                self._validate(type_, value)
        if self.path in self.config.temp:
            obj = None
            if self.index is None:
                obj = self.config.temp[self.path]
            elif str(self.index) in self.config.temp[self.path]:
                obj = self.config.temp[self.path][str(self.index)]
            if obj is not None:
                for attr in ['error', 'warnings', 'invalid', 'hasWarnings']:
                    if attr in obj:
                        del obj[attr]
        self.config.modify_value(self.path,
                                 self.index,
                                 value,
                                 remote,
                                 leader_old_value)
        self.config._check_raises_warnings(self.path, self.index, value, type_)

    def reset(self):
        self.config.delete_value(self.path,
                                 self.index)

    def default(self):
        if self.schema.get('isMulti'):
            if self.config.isfollower(self.path):
                if 'defaultmulti' in self.schema:
                    defaultmulti = self.schema['defaultmulti']
                else:
                    defaultmulti = None
                if self.index is not None:
                    value = defaultmulti
                else:
                    leader = next(iter(self.config.option(self.path.rsplit('.', 1)[0]).schema['properties']))
                    len_value = len(self.config.get_value(leader))
                    value = [defaultmulti] * len_value
            else:
                value = self.schema.get('value', [])
        else:
            value = self.schema.get('value')
        return value

    def valid(self):
        temp = self.config.temp.get(self.path, {})
        model = self.config.model.get(self.path, {})
        if self.index is None:
            if 'invalid' in temp:
                return not temp['invalid']
            return not model.get('invalid', False)
        elif str(self.index) in temp and 'invalid' in temp[str(self.index)]:
            return not temp[str(self.index)]['invalid']
        elif str(self.index) in model:
            return not model[str(self.index)].get('invalid', False)
        return True

    def warning(self):
        temp = self.config.temp.get(self.path, {})
        model = self.config.model.get(self.path, {})
        if self.index is None:
            if 'hasWarnings' in temp:
                return temp['hasWarnings']
            return model.get('hasWarnings', False)
        elif str(self.index) in temp and 'hasWarnings' in temp[str(self.index)]:
            return temp[str(self.index)]['hasWarnings']
        elif str(self.index) in model:
            return model[str(self.index)].get('hasWarnings', False)
        return False

    def error_message(self):
        temp = self.config.temp.get(self.path, {})
        model = self.config.model.get(self.path, {})
        if self.valid():
            return []
        if self.index is None:
            if temp.get('invalid') == True:
                return temp['error']
            return model['error']
        elif str(self.index) in temp and 'invalid' in temp[str(self.index)]:
            return temp[str(self.index)]['error']
        else:
            return model[str(self.index)]['error']
        return []

    def warning_message(self):
        temp = self.config.temp.get(self.path, {})
        model = self.config.model.get(self.path, {})
        if not self.warning():
            return []
        if self.index is None:
            if temp.get('hasWarnings') == True:
                return temp['warnings']
            return model['warnings']
        elif str(self.index) in temp and 'hasWarnings' in temp[str(self.index)]:
            return temp[str(self.index)]['warnings']
        else:
            return model[str(self.index)]['warnings']
        return []


class _Option:
    def list(self,
             type='option',
             recursive=False):
        if type not in ['all', 'option', 'optiondescription']:
            raise Exception('unknown list type {}'.format(type))
        for idx_path, path in enumerate(self.schema['properties']):
            subschema = self.schema['properties'][path]
            if not self.config.is_hidden(path, None):
                if subschema['type'] in ['object', 'array']:
                    if type in ['all', 'optiondescription']:
                        yield TiramisuOptionDescription(self.config,
                                                        subschema,
                                                        path)
                    if recursive:
                        yield from TiramisuOptionDescription(self.config,
                                                             subschema,
                                                             path).list(type, recursive)
                elif type in ['all', 'option']:
                    yield TiramisuOption(self.config,
                                         subschema,
                                         path,
                                         self.index)
            elif self.schema.get('type') == 'array' and idx_path == 0:
                # if a leader is hidden, follower are hidden too
                break



class TiramisuOptionDescription(_Option):
    # config.option(path) (with path == OptionDescription)
    def __init__(self,
                 config: 'Config',
                 schema: Dict,
                 path: str) -> None:
        self.config = config
        self.schema = schema
        self.path = path
        self.index = None

    def __getattr__(self,
                    subfunc: str) -> Any:
        if subfunc == 'option':
            return TiramisuOptionOption(self.config,
                                        self.path,
                                        self.schema)
        if subfunc == 'property':
            return TiramisuOptionProperty(self.config,
                                          self.path,
                                          None)
        if subfunc == 'value':
            return TiramisuOptionDescriptionValue(self.config,
                                                  self.schema,
                                                  self.path,
                                                  self.index)
        raise APIError(_('please specify a valid sub function ({})').format(subfunc))

    def group_type(self):
        if not self.config.is_hidden(self.path, None):
            # FIXME
            return 'default'
        raise PropertiesOptionError(None, {'disabled'}, None, opt_type='optiondescription')


class TiramisuLeadershipValue(TiramisuOptionValue):
    def len(self):
        return len(self.config.get_value(self.path))

    def pop(self,
            index: int) -> None:
        self.config.delete_value(self.path, index)


class TiramisuOption:
    # config.option(path) (with path == Option)
    def __init__(self,
                 config: 'Config',
                 schema: Dict,
                 path: str,
                 index: Optional[int]) -> None:
        self.config = config
        self.schema = schema
        self.path = path
        self.index = index

    def __getattr__(self,
                    subfunc: str) -> Any:
        if subfunc == 'option':
            if self.index != None:
                raise NotImplementedError()
            return TiramisuOptionOption(self.config,
                                        self.path,
                                        self.schema)
        if subfunc == 'value':
            if self.config.isleader(self.path):
                obj = TiramisuLeadershipValue
            else:
                obj = TiramisuOptionValue
            return obj(self.config,
                       self.schema,
                       self.path,
                       self.index)
        if subfunc == 'owner':
            return TiramisuOptionOwner(self.config,
                                       self.schema,
                                       self.path,
                                       self.index)
        if subfunc == 'property':
            return TiramisuOptionProperty(self.config,
                                          self.path,
                                          self.index)
        raise APIError(_('please specify a valid sub function ({})').format(subfunc))


class TiramisuContextProperty:
    # config.property
    def __init__(self,
                 config):
        self.config = config

    def get(self):
        return self.config.global_model.get('properties', [])


class ContextOption(_Option):
    # config.option
    def __init__(self,
                 config: 'Config',
                 schema: Dict) -> None:
        self.config = config
        self.schema = {'properties': schema}
        self.index = None 

    def __call__(self,
                 path: str,
                 index: Optional[int]=None) -> TiramisuOption:
        schema = self.config.get_schema(path)
        if schema['type'] in ['object', 'array']:
            return TiramisuOptionDescription(self.config,
                                             schema,
                                             path)
        return TiramisuOption(self.config,
                              schema,
                              path,
                              index)


class ContextOwner:
    # config.owner
    def __init__(self,
                 config: 'Config',
                 schema: Dict) -> None:
        self.config = config
        self.schema = {'properties': schema}
        self.index = None 

    def get(self):
        return self.config.global_model.get('owner', 'tmp')


class ContextValue(_Value):
    # config.value
    def __init__(self,
                 config: 'Config',
                 schema: Dict) -> None:
        self.config = config
        first = next(iter(schema.keys()))
        self.path = first.rsplit('.', 1)[0]
        self.schema = {'properties': schema}

    def __call__(self) -> TiramisuOptionValue:
        return TiramisuOptionValue(self.config,
                                   self.schema,
                                   path,
                                   index)

    def mandatory(self):
        for key, value in self.dict().items():
            if self.config.isfollower(key):
                if self.config.model.get(key, {}).get('null', {}).get('required'):
                    # FIXME test with index
                    if self.config.get_schema(key).get('isSubMulti'):
                        for val in value:
                            if not val or None in val or '' in val:
                                yield key
                                break
                    elif None in value or '' in value:
                        yield key
            elif self.config.get_schema(key).get('isMulti'):
                if self.config.model.get(key, {}).get('required') and (None in value or '' in value):
                    yield key
                if self.config.model.get(key, {}).get('needs_len') and not value:
                    yield key
            elif self.config.model.get(key, {}).get('required') and value is None:
                yield key


class Config:
    # config
    def __init__(self,
                 dico):
        if DEBUG:
            from pprint import pprint
            pprint(dico)
        if dico.get('version') != TIRAMISU_FORMAT:
            raise Exception('incompatible version of tiramisu (got {}, expected {})'.format(dico.get('version', '0.0'), TIRAMISU_FORMAT))
        self.model = dico.get('model')
        self.global_model = dico.get('global')
        self.form = dico.get('form')
        # support pattern
        if self.form:
            for key, option in self.form.items():
                if key != 'null' and 'pattern' in option:
                    option['pattern'] = re.compile(option['pattern'])
        self.temp = {}
        self.schema = dico.get('schema')
        self.updates = []
        if self.schema:
            first_path = next(iter(self.schema.keys()))
        else:
            first_path = ''
        if '.' in first_path:
            self.root = first_path.rsplit('.', 1)[0]
        else:
            self.root = ''

    def __getattr__(self,
                    subfunc: str) -> Any:
        if subfunc == 'property':
            return TiramisuContextProperty(self)
        if subfunc == 'option':
            return ContextOption(self,
                                 self.schema)
        if subfunc == 'value':
            return ContextValue(self,
                                self.schema)
        if subfunc == 'owner':
            return ContextOwner(self,
                                self.schema)
        raise APIError(_('please specify a valid sub function ({})').format(subfunc))

    def add_value(self,
                  path: str,
                  index: Optional[int],
                  value: Any,
                  remote: bool) -> None:
        if remote:
            self.manage_updates('add',
                                path,
                                index,
                                value)
        self.updates_value('add',
                           path,
                           index,
                           value,
                           remote)
        if not remote:
            self.manage_updates('add',
                                path,
                                index,
                                value)

    def modify_value(self,
                     path: str,
                     index: Optional[int],
                     value: Any,
                     remote: bool,
                     leader_old_value: Any) -> None:
        schema = self.get_schema(path)
        has_undefined = value is not None and isinstance(value, list) and undefined in value
        new_value = schema.get('defaultmulti')
        if not remote:
            if has_undefined:
                while undefined in value:
                    undefined_index = value.index(undefined)
                    schema_value = schema.get('value', [])
                    if len(schema_value) > undefined_index:
                        value[undefined_index] = schema_value[undefined_index]
                    else:
                        value[undefined_index] = new_value
            self.updates_value('modify',
                               path,
                               index,
                               value,
                               remote,
                               False,
                               leader_old_value)
            self.manage_updates('modify',
                                path,
                                index,
                                value)

        elif has_undefined:
            for idx, val in enumerate(value):
                self.manage_updates('modify',
                                    path,
                                    idx,
                                    val)
        else:
            self.manage_updates('modify',
                                path,
                                index,
                                value)
        if remote:
            self.updates_value('modify',
                               path,
                               index,
                               value,
                               remote,
                               False,
                               leader_old_value)

    def delete_value(self,
                     path: str,
                     index: Optional[int]) -> None:
        if self.get_schema(path)['type'] == 'symlink':
            raise ConfigError(_("can't delete a SymLinkOption"))
        remote = self.form.get(path, {}).get('remote', False)
        if remote:
            self.manage_updates('delete',
                                path,
                                index,
                                None)
        self.updates_value('delete',
                           path,
                           index,
                           None,
                           remote)
        if not remote:
            self.manage_updates('delete',
                                path,
                                index,
                                None)

    def get_properties(self,
                       model,
                       path,
                       index,
                       only_raises=True):
        props = model.get('properties', [])[:]
        if model.get('required'):
            if self.get_schema(path).get('isMulti', False) and not self.isfollower(path):
                props.append('empty')
            else:
                props.append('mandatory')
        if model.get('needs_len'):
            props.append('mandatory')
        if model.get('readOnly'):
            props.append('frozen')
        if only_raises and self.is_hidden(path,
                                           index):
            props.append('hidden')
        if self.form.get(path, {}).get('clearable'):
            props.append('clearable')
        return props

    def get_schema(self,
                   path):
        root_path = self.root
        schema = {'properties': self.schema,
                  'type': 'object'}
        if root_path:
            root = self.root.split('.')
            if not path.startswith(self.root):
                raise Exception('cannot find {0}'.format(path))
            subpaths = path.split('.')[len(root):]
        else:
            subpaths = path.split('.')
        current_subpath = 'root'
        for subpath in subpaths:
            if root_path:
                root_path += '.' + subpath
            else:
                root_path = subpath
            schema = schema['properties'].get(root_path)
            if schema is None:
                raise AttributeError(_('option "{0}" inconnue dans l\'optiondescription "{1}"').format(subpath, current_subpath))
            current_subpath = subpath
        return schema

    def isleader(self,
                 path):
        if '.' in path:
            parent_schema = self.get_schema(path.rsplit('.', 1)[0])
            if parent_schema['type'] == 'array':
                leader = next(iter(parent_schema['properties'].keys()))
                return leader == path
        return False


    def isfollower(self,
                   path: str) -> bool:
        if '.' in path:
            parent_schema = self.get_schema(path.rsplit('.', 1)[0])
            leader = next(iter(parent_schema['properties'].keys()))
            if parent_schema['type'] == 'array' and \
                    leader != path:
                return True
        return False

    def is_hidden(self,
                   path: str,
                   index: Optional[int],
                   permissive: bool=False) -> bool:
        if permissive:
            property_ = 'hidden'
            needs = True
            if property_ in self.global_model.get('permissives', []):
                return False
        else:
            property_ = 'display'
            needs = False
        if index is not None and property_ in self.temp.get(path, {}).get(str(index), {}):
            return self.temp[path][str(index)][property_] == needs
        if property_ in self.temp.get(path, {}):
            return self.temp[path][property_] == needs
        elif self.isfollower(path):
            if self.model.get(path, {}).get('null', {}).get(property_, None) == needs:
                return True
        elif self.model.get(path, {}).get(property_, None) == needs:
            return True
        if index is not None:
            index = str(index)
            if self.model.get(path, {}).get(index, {}).get(property_) == needs:
                return True
        return False

    def get_from_temp_model(self,
                            path,
                            index):
        if path in self.temp:
            is_delete = 'delete' in self.temp[path] and self.temp[path]['delete'] == True
            if index is not None and not is_delete and 'delete' in self.temp[path].get(index, {}):
                is_delete = self.temp[path][index]['delete'] == True
            if is_delete:
                return None
            if index is None and 'value' in self.temp[path] or 'value' in self.temp[path].get(index, {}):
                return self.temp[path]
        return self.model.get(path)

    def get_value(self,
                  path: str,
                  index: int=None) -> Any:
        schema = self.get_schema(path)
        if schema['type'] == 'symlink':
            path = schema['opt_path']
            schema = self.get_schema(path)
        if index is None:
            if self.isfollower(path):
                value = []
                parent_schema = self.get_schema(path.rsplit('.', 1)[0])
                leader = next(iter(parent_schema['properties'].keys()))
                leadership_len = len(self.get_value(leader))
                for idx in range(leadership_len):
                    val = self.get_value(path,
                                         idx)
                    self._check_raises_warnings(path, idx, val, schema['type'])
                    value.append(val)
            else:
                value = self.get_from_temp_model(path, index)
                if value is not None and 'value' in value:
                    value = value['value']
                else:
                    value = schema.get('value')
                if value is None and schema.get('isMulti', False):
                    value = []
        else:
            index = str(index)
            if self.isfollower(path):
                if self.is_hidden(path, index):
                    value = PropertiesOptionError(None, {'disabled'}, None, opt_type='option')
                else:
                    value = self.get_from_temp_model(path, index)
                    if value is not None and 'value' in value.get(index, {}):
                        value = value[index]['value']
                    else:
                        value = schema.get('defaultmulti')
            else:
                value = self.get_from_temp_model(path, index)
                if value is not None and index in value and 'value' in value[index]:
                    value = value[index]['value']
                else:
                    value = schema.get('default')
            if value is None and schema.get('isSubMulti', False):
                value = []
        if isinstance(value, list):
            value = value.copy()
        return value

    def get_owner(self,
                  path: str,
                  index: int) -> str:
        schema = self.get_schema(path)
        if schema['type'] == 'symlink':
            opt_path = schema['opt_path']
            index = str(index)
            if self.is_hidden(opt_path, index):
                raise PropertiesOptionError(None, {'disabled'}, None, opt_type='option')
            return self.get_owner(opt_path, index)
        elif not self.isfollower(path):
            if 'owner' in self.temp.get(path, {}):
                owner = self.temp[path]['owner']
            else:
                owner = self.model.get(path, {}).get('owner', 'default')
        else:
            index = str(index)
            if self.is_hidden(path, index):
                raise PropertiesOptionError(None, {'disabled'}, None, opt_type='option')
            value = self.get_from_temp_model(path, index)
            if value is not None and 'owner' in value.get(index, {}):
                owner = value[index]['owner']
            else:
                owner = 'default'
        return owner

    def manage_updates(self,
                       action,
                       path,
                       index,
                       value):
        update_last_action = False
        if self.updates:
            last_body = self.updates[-1]
            if last_body['name'] == path:
                if index is None and not 'index' in last_body:
                    last_action = last_body['action']
                    if last_action == action or \
                            last_action in ['delete', 'modify'] and action in ['delete', 'modify']:
                        update_last_action = True
                elif index == None and action == 'delete':
                    for update in reversed(self.updates):
                        if update['name'] == path:
                            del self.updates[-1]
                        else:
                            break
                elif last_body.get('index') == index:
                    if last_body['action'] == 'add' and action == 'modify':
                        action = 'add'
                        update_last_action = True
                    elif last_body['action'] == action and action != 'delete' or \
                            last_body['action'] == 'modify' and action == 'delete':
                        update_last_action = True
                    elif last_body['action'] == 'add' and action == 'delete':
                        del self.updates[-1]

        if update_last_action:
            if action == 'delete' and value is None:
                if 'value' in last_body:
                    del last_body['value']
            else:
                last_body['value'] = value
            if index is None and 'index' in last_body:
                del last_body['index']
            last_body['action'] = action
        else:
            data = {'action': action,
                    'name': path}
            if action != 'delete' and value is not undefined:
                data['value'] = value
            if index is not None:
                data['index'] = index
            self.updates.append(data)

    def send(self):
        if DEBUG:
            print('<===== send')
            print(self.updates)
        self.send_data({'updates': self.updates,
                        'model': self.model})

    def updates_value(self,
                      action: str,
                      path: str,
                      index: Optional[int],
                      value: Optional[Any],
                      remote: bool,
                      default_value: bool=False,
                      leader_old_value: Optional[Any]=undefined) -> None:
        # if 'pattern' in self.form.get(path, {}) and (not isinstance(value, list) or undefined not in value) and not self.test_value(path, index, value, remote):
        #     return
        if remote:
            self.send()
        else:
            changes = []
            if self.test_value(path, index, value) and not self.is_hidden(path, index):
                changes.append(path)
            if path in self.model and (index is None or str(index) in self.model[path]):
                model = self.model[path]
                if index is not None:
                    model = model[str(index)]
                if 'warnings' in model:
                    del model['warnings']
                if 'error' in model:
                    del model['error']
            if action == 'delete':
                if self.option(path).option.isleader():
                    # if remove an indexed leader value
                    if index is not None:
                        leader_value = self.option(path).value.get()
                        leader_value.pop(index)
                        owner = self.global_model.get('owner', 'tmp')
                    else:
                        leader_value = self.default_value(path)
                        owner = 'default'
                    max_value = len(leader_value) + 1
                    self._set_temp_value(path, None, leader_value, owner)
                    leadership_path = path.rsplit('.', 1)[0]
                    parent_schema = self.get_schema(leadership_path)
                    iter_leadership = list(parent_schema['properties'].keys())
                    for follower in iter_leadership[1:]:
                        # remove value for this index and reduce len
                        new_temp = {}
                        for idx in range(max_value):
                            cur_index = idx
                            if index is not None:
                                if index == idx:
                                    continue
                                if index < cur_index:
                                    cur_index -= 1
                            if 'delete' in self.temp.get(follower, {}):
                                #FIXME copier les attributs hidden, ... depuis self.temp[follower][index] ?
                                new_temp[str(cur_index)] = {'delete': True}
                            elif self.temp.get(follower, {}).get(str(idx)) is not None:
                                if index is None or index == idx:
                                    new_temp[str(cur_index)] = {'delete': True}
                                else:
                                    new_temp[str(cur_index)] = self.temp[follower][str(idx)]
                            elif self.model.get(follower, {}).get(str(idx)) is not None:
                                if index is None or index == idx:
                                    new_temp[str(cur_index)] = {'delete': True}
                                else:
                                    new_temp[str(cur_index)] = self.model[follower][str(idx)]
                        if self.model.get(follower, {}).get(str(max_value)) is not None:
                            # FIXME copier les attributs hidden, ... depuis self.temp[follower][index] ?
                            new_temp[str(max_value)] = {'delete': True}
                        self.temp[follower] = new_temp
                    value = leader_value
                    index = None
                elif index is None:
                    self._del_temp_value(path, index)
                    value = self.get_value(path)
                else:
                    # it's a follower with index
                    self.temp.setdefault(path, {})[str(index)] = {'delete': True}
                    self._del_temp_value(path, index)
                    value = self.get_value(path, index)
                default_value = True
            elif index is None:
                # set a value for a not follower option
                self.set_not_equal(path, value, index)
                if default_value is True:
                    self.model[path]['value'] = value
                else:
                    self._set_temp_value(path, None, value, self.global_model.get('owner', 'tmp'))
            else:
                self.set_not_equal(path, value, index)
                # set a value for a follower option
                if default_value is True:
                    self.model[path][str(index)]['value'] = value
                else:
                    self._set_temp_value(path, index, value, self.global_model.get('owner', 'tmp'))
            if not self.is_hidden(path, index):
                changes.append(path)
            self.set_dependencies(path, value, False, changes, index)
            self.do_copy(path, index, value, changes)
            if leader_old_value is not undefined and len(leader_old_value) < len(value):
                # if leader and length is change, display/hide follower from follower's default value
                index = len(value) - 1
                parent_path = '.'.join(path.split('.')[:-1])
                followers = list(self.option(parent_path).list())[1:]
                for follower in followers:
                    follower_path = follower.option.path()
                    try:
                        follower_value = self.option(follower_path, index).value.get()
                        self.set_dependencies(follower_path, follower_value, None, index)
                    except PropertiesOptionError:
                        pass
            for path in changes:
                self.send_event('tiramisu-change', path)

    def _set_temp_value(self, path, index, value, owner):
        if index is not None:
            obj = self.temp.setdefault(path, {}).setdefault(str(index), {})
        else:
            obj = self.temp.setdefault(path, {})
        if 'delete' in obj:
            del obj['delete']
        obj['value'] = value
        obj['owner'] = owner

    def _del_temp_value(self, path, index):
        if index is not None:
            obj = self.temp.setdefault(path, {}).setdefault(str(index), {})
        else:
            obj = self.temp.setdefault(path, {})
        for key in ['value', 'owner']:
            if key in obj:
                del obj[key]
        obj['delete'] = True

    def default_value(self, path):
        schema = self.get_schema(path)
        value = schema.get('value')
        if value is None and schema.get('isMulti', False):
            value = []
        elif isinstance(value, list):
            value = value.copy()
        return value

    def updates_data(self, data):
        if DEBUG:
            from pprint import pprint
            print('====> updates_data')
            pprint(data)
        self.updates = []
        self.temp.clear()
        self.model = data['model']
        for path in data['updates']:
            self.send_event('tiramisu-change', path)

    def test_value(self,
                   path: str,
                   index: Optional[int],
                   value: Any) -> bool:
        if isinstance(value, list):
            for val in value:
                if not self._test_value(path, index, val):
                    # when a value is invalid, all are invalid
                    return False
            return True
        return not self._test_value(path, index, value)

    def _test_value(self,
                    path: str,
                    index:Optional[int],
                    value: Any) -> bool:
        if not path in self.form or not 'pattern' in self.form[path]:
            return True
        if value is None or value is '':
            match = True
        else:
            if isinstance(value, int):
                value = str(value)
            match = self.form[path]['pattern'].search(value) is not None
        if not path in self.temp:
            self.temp[path] = {}
        if index is None:
            if not match:
                self.temp[path]['invalid'] = True
                self.temp[path]['error'] = ['invalid value']
            else:
                self.temp[path]['invalid'] = False
        else:
            if not str(index) in self.temp[path]:
                self.temp[path][str(index)] = {}
            if not match:
                self.temp[path][str(index)]['invalid'] = True
                self.temp[path][str(index)]['error'] = ['invalid value']
            else:
                self.temp[path][str(index)]['invalid'] = False
        return match

    def set_dependencies(self,
                         path: str,
                         ori_value: Any,
                         force_hide: bool,
                         changes: List,
                         index: Optional[int]=None) -> None:
        dependencies = self.form.get(path, {}).get('dependencies', {})
        if dependencies:
            if not isinstance(ori_value, list):
                self._set_dependencies(path, ori_value, dependencies, force_hide, changes, index)
            else:
                for idx, ori_val in enumerate(ori_value):
                    self._set_dependencies(path, ori_val, dependencies, force_hide, changes, idx)

    def _set_dependencies(self,
                          path: str,
                          ori_value: Any,
                          dependencies: Dict,
                          force_hide: bool,
                          changes: List,
                          index: Optional[int]) -> None:
                if ori_value in dependencies['expected']:
                    expected = dependencies['expected'][ori_value]
                else:
                    expected = dependencies['default']
                for action in ['hide', 'show']:
                    expected_actions = expected.get(action)
                    if expected_actions:
                        if force_hide:
                            display = True
                        else:
                            display = action == 'show'
                        for expected_path in expected_actions:
                            if expected_path not in self.temp:
                                self.temp[expected_path] = {}
                            old_hidden = self.is_hidden(expected_path,
                                                        index)
                            leader_path = None
                            if index is not None:
                                if str(index) not in self.temp[expected_path]:
                                    self.temp[expected_path][str(index)] = {}
                                self.temp[expected_path][str(index)]['display'] = display
                            else:
                                self.temp[expected_path]['display'] = display
                                schema = self.get_schema(expected_path)
                                if schema['type'] == 'array':
                                    leader_path = next(iter(schema['properties'].keys()))
                                    if leader_path not in self.temp:
                                        self.temp[leader_path] = {}
                                    self.temp[leader_path]['display'] = display
                            if old_hidden == display:
                                if  expected_path not in changes:
                                    changes.append(expected_path)
                                if leader_path not in changes:
                                    changes.append(leader_path)
                            value = self.get_value(expected_path, index)
                            self.set_dependencies(expected_path, value, not display, changes, index)

    def set_not_equal(self,
                      path: str,
                      value: Any,
                      index: Optional[int]) -> None:
        not_equals = self.form.get(path, {}).get('not_equal', [])
        if not_equals:
            vals = []
            opts = []
            if isinstance(value, list):
                for val in value:
                    vals.append(val)
                    opts.append(path)
            else:
                vals.append(value)
                opts.append(path)
            for not_equal in not_equals:
                for path_ in not_equal['options']:
                    if self.is_hidden(path_, index, permissive=True):
                        raise PropertiesOptionError(None, {'hidden'}, None, opt_type='option')
                    schema = self.get_schema(path_)
                    p_value = self.get_value(path_)
                    if isinstance(p_value, list):
                        for val in p_value:
                            vals.append(val)
                            opts.append(path_)
                    else:
                        vals.append(p_value)
                        opts.append(path_)
                equal = []
                warnings_only = not_equal.get('warnings', False)
                if warnings_only and 'warnings' not in self.global_model.get('properties', []):
                    continue
                if warnings_only:
                    msg = _('should be different from the value of {}')
                    #msgcurr = _('value for {} should be different')
                else:
                    msg = _('must be different from the value of {}')
                    #msgcurr = _('value for {} must be different')
                for idx_inf, val_inf in enumerate(vals):
                    for idx_sup, val_sup in enumerate(vals[idx_inf + 1:]):
                        if val_inf == val_sup is not None:
                            for opt_ in [opts[idx_inf], opts[idx_inf + idx_sup + 1]]:
                                if opt_ not in equal:
                                    equal.append(opt_)
                if equal:
                    equal_name = {}
                    display_equal = []
                    for opt_ in equal:
                        display_equal.append('"' + self.get_schema(opt_)['title'] + '"')
                    display_equal = display_list(display_equal)
                    msg_ = msg.format(display_equal)
                    is_demoting_error_warning = 'demoting_error_warning' in self.global_model.get('properties', [])
                    if warnings_only or is_demoting_error_warning:
                        paths = not_equal['options'] + [path]
                    else:
                        paths = [path]
                    for path_ in paths:
                        if path_ not in self.temp:
                            self.temp[path_] = {}
                        temp = self.temp[path_]
                        if index is not None:
                            if str(index) not in temp:
                                temp[str(index)] = {}
                            temp = temp[str(index)]
                        if warnings_only:
                            temp['hasWarnings'] = True
                            temp.setdefault('warnings', []).append(msg_)
                        else:
                            if not is_demoting_error_warning:
                                raise ValueError(msg)
                            temp['invalid'] = True
                            temp.setdefault('error', []).append(msg_)

    def do_copy(self,
                path: str,
                index: Optional[int],
                value: Any,
                changes: List) -> None:
        copy = self.form.get(path, {}).get('copy')
        if copy:
            for opt in copy:
                owner = self.get_owner(opt, index)
                if owner == 'default':
                    # do not change in self.temp, it's default value
                    if self.model[opt]['value'] != value:
                        if isinstance(value, list):
                            value = value.copy()
                        # self.model[opt]['value'] = value
                        remote = self.form.get(opt, {}).get('remote', False)
                        self.updates_value('modify', opt, index, value, remote, True)
                        if not self.is_hidden(opt, index) and opt not in changes:
                            changes.append(opt)


    def _check_raises_warnings(self, path, index, value, type, withwarning=True):
        subconfig_value = self.option(path, index).value
        if not subconfig_value.valid():
            is_demoting_error_warning = 'demoting_error_warning' in self.global_model.get('properties', [])
            for err in subconfig_value.error_message():
                if is_demoting_error_warning:
                    warnings.warn_explicit(ValueErrorWarning(value,
                                                             type,
                                                             Option(path, path),
                                                             '{0}'.format(err),
                                                             index),
                                           ValueErrorWarning,
                                           'Option', 0)
                else:
                    if path not in self.temp:
                        self.temp[path] = {}
                    if index is None:
                        obj = self.temp[path]
                    else:
                        if str(index) not in self.temp[path]:
                            self.temp[path][str(index)] = {}
                        obj = self.temp[path][str(index)]
                    obj['invalid'] = False
                    raise ValueError(err)

        if withwarning and subconfig_value.warning():
            for warn in subconfig_value.warning_message():
                warnings.warn_explicit(ValueErrorWarning(value,
                                                         type,
                                                         Option(path, path),
                                                         '{0}'.format(warn),
                                                         index),
                                       ValueErrorWarning,
                                       'Option', 0)

    def send_data(self,
                  updates):
        raise NotImplementedError('please implement send_data method')

    def send_event(self,
                   evt: str,
                   path: str):
        pass
