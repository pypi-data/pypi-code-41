# -*- coding: utf-8 -*-

import warnings
import sys
from copy import copy
from itertools import chain
from .error import ValueWarning, ValueErrorWarning, PropertiesOptionError, ConfigError
from .setting import undefined
from . import SynDynOption, RegexpOption, ChoiceOption, ParamContext, ParamOption
from .i18n import _


TYPES = {'SymLinkOption': 'symlink',
         'IntOption': 'integer',
         'FloatOption': 'integer',
         'ChoiceOption': 'choice',
         'BoolOption': 'boolean',
         'PasswordOption': 'password',
         'PortOption': 'integer',
         'DateOption': 'date',
         'DomainnameOption': 'domainname',
         'StrOption': 'string'
         }
INPUTS = ['string',
          'integer',
          'filename',
          'password',
          'email',
          'username',
          'ip',
          'domainname']


# return always warning (even if same warning is already returned)
warnings.simplefilter("always", ValueWarning)
warnings.simplefilter("always", ValueErrorWarning)


class Callbacks(object):
    def __init__(self, tiramisu_web):
        self.tiramisu_web = tiramisu_web
        self.clearable = tiramisu_web.clearable
        self.remotable = tiramisu_web.remotable
        self.callbacks = []

    def add(self,
            path,
            childapi,
            schema,
            force_store_value):
        if self.remotable == 'all' or childapi.option.isoptiondescription():
            return
        callback, callback_params = childapi.option.callbacks()
        if callback is None:  # FIXME ? and force_store_value and self.clearable != 'all':
            return
        self.callbacks.append((callback, callback_params, path, childapi, schema, force_store_value))

    def process_properties(self, form):
        for callback, callback_params, path, childapi, schema, force_store_value in self.callbacks:
            if childapi.option.isfollower():
                self.tiramisu_web.set_remotable(path, form, childapi)
                continue
            has_option = False
            if callback_params is not None:
                for callback_param in chain(callback_params.args, callback_params.kwargs.values()):
                    if isinstance(callback_param, ParamContext):
                        raise ValueError(_('context is not supported from now for {}').format(path))
                    if isinstance(callback_param, ParamOption):
                        has_option = True
                        if callback.__name__ != 'tiramisu_copy' or 'expire' in childapi.option.properties():
                            self.tiramisu_web.set_remotable(callback_param.option.impl_getpath(), form)
            if not has_option and form.get(path, {}).get('remote', False) == False:
                if 'expire' in childapi.option.properties():
                    self.tiramisu_web.set_remotable(path, form, childapi)
                elif childapi.owner.isdefault():
                    # get calculated value and set clearable
                    schema[path]['value'] = childapi.value.get()
                    if self.clearable == 'minimum':
                        form.setdefault(path, {})['clearable'] = True

    def manage_callbacks(self, form):
        for callback, callback_params, path, childapi, schema, force_store_value in self.callbacks:
            if callback_params is not None:
                for callback_param in chain(callback_params.args, callback_params.kwargs.values()):
                    if isinstance(callback_param, ParamOption) and callback.__name__ == 'tiramisu_copy':
                        opt_path = callback_param.option.impl_getpath()
                        if form.get(opt_path, {}).get('remote') is not True:
                            form.setdefault(opt_path, {})
                            form[opt_path].setdefault('copy', []).append(path)

    def process(self,
                form):
        self.process_properties(form)
        self.manage_callbacks(form)


class Consistencies(object):
    def __init__(self, tiramisu_web):
        self.not_equal = {}
        self.tiramisu_web = tiramisu_web

    def add(self, path, childapi, form):
        if not childapi.option.isoptiondescription():
            for consistency in childapi.option.consistencies():
                cons_id, func, all_cons_opts, params = consistency
                if func == '_cons_not_equal' and params.get('transitive', True) is True:
                    options_path = []
                    for option in all_cons_opts:
                        options_path.append(option()._path)
                    for idx, option in enumerate(all_cons_opts):
                        option = option()
                        paths = options_path.copy()
                        paths.pop(idx)
                        warnings_only = params.get('warnings_only') or getattr(option, '_warnings_only', False)
                        self.not_equal.setdefault(option._path, {}).setdefault(warnings_only, []).extend(paths)
                else:
                    for option in all_cons_opts:
                        self.tiramisu_web.set_remotable(option()._path, form)

    def process(self, form):
        for path in self.not_equal:
            if self.tiramisu_web.is_remote(path, form):
                continue
            if path not in form:
                form[path] = {}
            for warnings_only in self.not_equal[path]:
                options = self.not_equal[path][warnings_only]
                if 'not_equal' not in form[path]:
                    form[path]['not_equal'] = []
                obj = {'options': options}
                if warnings_only:
                    obj['warnings'] = True
                form[path]['not_equal'].append(obj)


class Requires(object):
    def __init__(self, tiramisu_web):
        self.requires = {}
        self.options = {}
        self.tiramisu_web = tiramisu_web
        self.action_hide = self.tiramisu_web.config._config_bag.properties

    def set_master_remote(self, childapi, path, form):
        if childapi.option.isoptiondescription():
            isfollower = False
        else:
            isfollower = childapi.option.isfollower()
        if isfollower:
            parent_path = path.rsplit('.', 1)[0]
            parent = self.tiramisu_web.config.unrestraint.option(parent_path)
            leader = next(parent.list())
            self.tiramisu_web.set_remotable(leader.option.path(), form, leader)

    def manage_requires(self,
                        childapi,
                        path,
                        form,
                        current_action):
        for requires in childapi.option.requires():
            len_to_long = len(requires) > 1
            for require in requires:
                options, action, inverse, transitive, same_action, operator = require
                if not len_to_long:
                    len_to_long = len(options) > 1
                for option, expected in options:
                    if isinstance(option, tuple):
                        for option_param in chain(option[1].args, option[1].kwargs.values()):
                            if isinstance(option_param, ParamOption):
                                self.tiramisu_web.set_remotable(option_param.option.impl_getpath(), form)
                        self.set_master_remote(childapi, path, form)
                    elif len_to_long:
                        self.tiramisu_web.set_remotable(option.impl_getpath(), form)
                        self.set_master_remote(childapi, path, form)
                    else:
                        option_path = option.impl_getpath()
                        if action in self.action_hide:
                            require_option = self.tiramisu_web.config.unrestraint.option(option_path)
                            if transitive is False or same_action is False or operator == 'and':
                                # transitive to "False" not supported yet for a requirement
                                # same_action to "False" not supported yet for a requirement
                                # operator "and" not supported yet for a requirement
                                self.tiramisu_web.set_remotable(option_path, form, require_option)
                                self.set_master_remote(childapi, path, form)
                            if require_option.option.requires():
                                for reqs in require_option.option.requires():
                                    for req in reqs:
                                        for subopt, subexp in req[0]:
                                            if not isinstance(subopt, tuple):
                                                self.tiramisu_web.set_remotable(subopt.impl_getpath(), form)
                                                self.set_master_remote(childapi, path, form)
                            if inverse:
                                act = 'show'
                                inv_act = 'hide'
                            else:
                                act = 'hide'
                                inv_act = 'show'
                            if isinstance(option, ChoiceOption):
                                require_option = self.tiramisu_web.config.unrestraint.option(option_path)
                                values = self.tiramisu_web.get_enum(require_option,
                                                                    require_option.option.ismulti(),
                                                                    option_path,
                                                                    require_option.option.properties())
                                for value in values:
                                    if value not in expected:
                                        self.requires.setdefault(path,
                                                                  {'expected': {}}
                                                                 )['expected'].setdefault(value,
                                                                                          {}).setdefault(inv_act,
                                                                                                         []).append(option_path)
                            if current_action is None:
                                current_action = action
                            elif current_action != action:
                                self.tiramisu_web.set_remotable(option_path, form)
                                self.set_master_remote(childapi, path, form)
                            for exp in expected:
                                self.requires.setdefault(path,
                                                         {'expected': {}}
                                                         )['expected'].setdefault(exp,
                                                                                  {}).setdefault(act,
                                                                                                 []).append(option_path)
                            self.requires[path].setdefault('default', {}).setdefault(inv_act, []).append(option_path)
                        else:
                            self.tiramisu_web.set_remotable(option_path, form)
                            self.set_master_remote(childapi, path, form)

    def add(self, path, childapi, form):
        #collect id of all options
        child = childapi.option.get()
        if isinstance(child, SynDynOption):
            child = child._impl_getopt()
        self.options[child] = path
        current_action = None

        self.manage_requires(childapi,
                             path,
                             form,
                             current_action)

    def process(self, form):
        dependencies = {}
        for path, values in self.requires.items():
            if 'default' in values:
                for option in values['default'].get('show', []):
                    if path == option:
                        self.tiramisu_web.set_remotable(path, form)
                    if not self.tiramisu_web.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'default': {}, 'expected': {}}
                                                )['default'].setdefault('show', [])
                        if path not in dependencies[option]['default']['show']:
                            dependencies[option]['default']['show'].append(path)
                for option in values['default'].get('hide', []):
                    if path == option:
                        self.tiramisu_web.set_remotable(path, form)
                    if not self.tiramisu_web.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'default': {}, 'expected': {}}
                                                )['default'].setdefault('hide', [])
                        if path not in dependencies[option]['default']['hide']:
                            dependencies[option]['default']['hide'].append(path)
            for expected, actions in values['expected'].items():
                if expected is None:
                    expected = ''
                for option in actions.get('show', []):
                    if path == option:
                        self.tiramisu_web.set_remotable(path, form)
                    if not self.tiramisu_web.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'expected': {}}
                                                )['expected'].setdefault(expected,
                                                                         {}).setdefault('show', [])
                        if path not in dependencies[option]['expected'][expected]['show']:
                            dependencies[option]['expected'][expected]['show'].append(path)
                for option in actions.get('hide', []):
                    if path == option:
                        self.tiramisu_web.set_remotable(path, form)
                    if not self.tiramisu_web.is_remote(option, form):
                        dependencies.setdefault(option,
                                                {'expected': {}}
                                                )['expected'].setdefault(expected,
                                                                         {}).setdefault('hide', [])
                        if path not in dependencies[option]['expected'][expected]['hide']:
                            dependencies[option]['expected'][expected]['hide'].append(path)
        for path, dependency in dependencies.items():
            form.setdefault(path, {})['dependencies'] = dependency


class TiramisuDict:

    # propriete:
    #   hidden
    #   mandatory
    #   editable

    # FIXME model:
    # #optionnel mais qui bouge
    # choices/suggests
    # warning
    #
    # #bouge
    # owner
    # properties

    def __init__(self,
                 config,
                 root=None,
                 clearable="all",
                 remotable="minimum"):
        self.config = config
        self.root = root
        self.requires = None
        self.callbacks = None
        self.consistencies = None
        #all, minimum, none
        self.clearable = clearable
        #all, minimum, none
        self.remotable = remotable
        self.context_properties = self.config.property.get()
        self.context_permissives = self.config.permissive.get()

    def add_help(self,
                 obj,
                 childapi):
        hlp = childapi.information.get('help', None)
        if hlp is not None:
            obj['help'] = hlp

    def get_list(self, root, subchildapi):
        for childapi in subchildapi.list('all'):
            childname = childapi.option.name()
            if root is None:
                path = childname
            else:
                path = root + '.' + childname
            yield path, childapi

    def is_remote(self, path, form):
        if self.remotable == 'all':
            return True
        else:
            return path in form and form[path].get('remote', False) == True

    def set_remotable(self, path, form, childapi=None):
        if self.remotable == 'none':
            raise ValueError(_('option {} only works when remotable is not "none"').format(path))
        form.setdefault(path, {})['remote'] = True
        if childapi is None:
            childapi = self.config.unrestraint.option(path)
        if childapi.option.isfollower():
            parent_path = path.rsplit('.', 1)[0]
            parent = self.config.unrestraint.option(parent_path)
            leader = next(parent.list())
            form.setdefault(leader.option.path(), {})['remote'] = True

    def walk(self,
             root,
             subchildapi,
             schema,
             model,
             form,
             order,
             updates_status,
             init=False):
        error = None
        if init:
            if form is not None:
                self.requires = Requires(self)
                self.consistencies = Consistencies(self)
                self.callbacks = Callbacks(self)
        else:
            init = False
        try:
            if subchildapi is None:
                if root is None:
                    subchildapi = self.config.unrestraint.option
                else:
                    subchildapi = self.config.unrestraint.option(root)
                isleadership = False
            else:
                isleadership = subchildapi.option.isleadership()
            leader_len = None
            for path, childapi in self.get_list(root, subchildapi):
                if isleadership and leader_len is None:
                    leader_len = childapi.value.len()
                    one_is_remote = False
                props_no_requires = set(childapi.option.properties())
                if form is not None:
                    self.requires.add(path,
                                      childapi,
                                      form)
                    self.consistencies.add(path,
                                           childapi,
                                           form)
                    self.callbacks.add(path,
                                       childapi,
                                       schema,
                                       'force_store_value' in props_no_requires)
                childapi_option = childapi.option
                if model is not None and childapi.option.isoptiondescription() or not childapi_option.issymlinkoption():
                    self.gen_model(model,
                                   childapi,
                                   path,
                                   leader_len,
                                   updates_status)
                if order is not None:
                    order.append(path)
                if childapi.option.isoptiondescription():
                    web_type = 'optiondescription'
                    if childapi_option.isleadership():
                        type_ = 'array'
                    else:
                        type_ = 'object'
                    if schema is not None:
                        schema[path] = {'properties': {},
                                        'type': type_}
                        subschema = schema[path]['properties']
                    else:
                        subschema = schema
                    self.walk(path,
                              childapi,
                              subschema,
                              model,
                              form,
                              order,
                              updates_status)
                else:
                    child = childapi_option.get()
                    childtype = child.__class__.__name__
                    if childtype == 'SynDynOption':
                        childtype = child._impl_getopt().__class__.__name__
                    if childapi_option.issymlinkoption():
                        web_type = 'symlink'
                        value = None
                        defaultmulti = None
                        is_multi = False
                    else:
                        web_type = childapi_option.type()
                        value = childapi.option.default()
                        if value == []:
                            value = None

                        is_multi = childapi_option.ismulti()
                        if is_multi:
                            defaultmulti = childapi_option.defaultmulti()
                            if defaultmulti == []:
                                defaultmulti = None
                        else:
                            defaultmulti = None

                    if schema is not None:
                        self.gen_schema(schema,
                                        childapi,
                                        childapi_option,
                                        path,
                                        props_no_requires,
                                        value,
                                        defaultmulti,
                                        is_multi,
                                        web_type,
                                        form)
                    if form is not None:
                        self.gen_form(form,
                                      web_type,
                                      path,
                                      child,
                                      childapi_option,
                                      childtype)
                if schema is not None:
                    if web_type != 'symlink':
                        schema[path]['title'] = childapi_option.description()
                    self.add_help(schema[path],
                                  childapi)
        except Exception as err:
            # import traceback
            # traceback.print_exc()
            if not init:
                raise err
            error = err
        if init and form is not None:
            self.callbacks.process(form)
            self.requires.process(form)
            self.consistencies.process(form)
            del self.requires
            del self.consistencies
            del self.callbacks
        if error:
            msg = str(error)
            del error
            raise ConfigError(_('unable to transform tiramisu object to dict: {}').format(msg))


    def gen_schema(self,
                   schema,
                   childapi,
                   childapi_option,
                   path,
                   props_no_requires,
                   value,
                   defaultmulti,
                   is_multi,
                   web_type,
                   form):
        schema[path] = {'type': web_type}
        if childapi_option.issymlinkoption():
            schema[path]['opt_path'] = childapi_option.get().impl_getopt().impl_getpath()
        else:
            if defaultmulti is not None:
                schema[path]['defaultmulti'] = defaultmulti

            if is_multi:
                schema[path]['isMulti'] = is_multi

            if childapi_option.issubmulti():
                schema[path]['isSubMulti'] = True

            if 'auto_freeze' in props_no_requires:
                schema[path]['autoFreeze'] = True

            if web_type == 'choice':
                values, values_params = childapi.value.callbacks()
                if values_params:
                    for values_param in chain(values_params.args, values_params.kwargs.values()):
                        if isinstance(values_param, ParamOption):
                            self.set_remotable(path, form, childapi)
                            return
                schema[path]['enum'] = self.get_enum(childapi,
                                                     is_multi,
                                                     path,
                                                     props_no_requires)
            if value is not None and not self.is_remote(path, form):
                schema[path]['value'] = value


    def get_enum(self,
                 childapi,
                 is_multi,
                 path,
                 props_no_requires):
        values = childapi.value.list()
        empty_is_required = not childapi.option.isfollower() and is_multi
        if '' not in values and ((empty_is_required and not 'empty' in props_no_requires) or \
                (not empty_is_required and not 'mandatory' in props_no_requires)):
            values = [''] + list(values)
        return values

    def gen_form(self,
                 form,
                 web_type,
                 path,
                 child,
                 childapi_option,
                 childtype):
        obj_form = {}
        if path in form:
            obj_form.update(form[path])
        if not childapi_option.issymlinkoption():
            if childapi_option.validator() != (None, None):
                obj_form['remote'] = True
                params = childapi_option.validator()[1]
                if params is not None:
                    for param in chain(params.args, params.kwargs.values()):
                        if isinstance(param, ParamContext):
                            raise ValueError(_('context is not supported from now for {}').format(path))
                        if isinstance(param, ParamOption):
                            self.set_remotable(param.option.impl_getpath(), form)
            if self.clearable == 'all':
                obj_form['clearable'] = True
            if self.clearable != 'none':
                obj_form['clearable'] = True
            if self.remotable == 'all' or childapi_option.has_dependency():
                obj_form['remote'] = True
            if childtype == 'IPOption' and (child.impl_get_extra('_private_only') or not child.impl_get_extra('_allow_reserved') or child.impl_get_extra('_cidr')):
                obj_form['remote'] = True
            if childtype == 'DateOption':
                obj_form['remote'] = True
            if not obj_form.get('remote', False):
                pattern = childapi_option.pattern()
                if pattern is not None:
                    obj_form['pattern'] = pattern
                if childtype == 'PortOption':
                    obj_form['min'] = child.impl_get_extra('_min_value')
                    obj_form['max'] = child.impl_get_extra('_max_value')
            if childtype == 'FloatOption':
                obj_form['step'] = 'any'
            if web_type == 'choice':
                obj_form['type'] = 'choice'
            elif web_type in INPUTS:
                obj_form['type'] = 'input'
            if obj_form:
                form[path] = obj_form

    def calc_raises_properties(self,
                               obj,
                               childapi):
        old_properties = childapi._option_bag.config_bag.properties
        del childapi._option_bag.config_bag.properties
        has_permissive = 'permissive' in childapi._option_bag.config_bag.properties
        if not has_permissive:
            childapi._option_bag.config_bag.properties = childapi._option_bag.config_bag.properties | {'permissive'}
        # 'display=False' means cannot access only without permissive option
        # 'hidden=True' means cannot access with or without permissive option
        properties = childapi.property.get(only_raises=True)
        if has_permissive:
            properties -= self.config.permissive.get()
        properties -= childapi.permissive.get()
        if properties:
            obj['hidden'] = True
        childapi._option_bag.config_bag.properties = childapi._option_bag.config_bag.properties - {'permissive'}
        properties = childapi.property.get(only_raises=True)
        if has_permissive:
            properties -= self.config.permissive.get()
        properties -= childapi.permissive.get()
        if properties:
            obj['display'] = False
        childapi._option_bag.config_bag.properties = old_properties

    def _gen_model_properties(self,
                              childapi,
                              path,
                              index):
        isfollower = childapi.option.isfollower()
        props = set(childapi.property.get())
        obj = self.gen_properties(props,
                                  isfollower,
                                  childapi.option.ismulti(),
                                  index)
        self.calc_raises_properties(obj, childapi)
        return obj

    def gen_properties(self,
                       properties,
                       isfollower,
                       ismulti,
                       index):
        obj = {}
        if not isfollower and ismulti:
            if 'empty' in properties:
                if index is None:
                    obj['required'] = True
                properties.remove('empty')
            if 'mandatory' in properties:
                if index is None:
                    obj['needs_len'] = True
                properties.remove('mandatory')
        elif 'mandatory' in properties:
            if index is None:
                obj['required'] = True
            properties.remove('mandatory')
        if 'frozen' in properties:
            if index is None:
                obj['readOnly'] = True
            properties.remove('frozen')
        if 'hidden' in properties:
            properties.remove('hidden')
        if 'disabled' in properties:
            properties.remove('disabled')
        if properties:
            lprops = list(properties)
            lprops.sort()
            obj['properties'] = lprops
        return obj

    def gen_model(self,
                  model,
                  childapi,
                  path,
                  leader_len,
                  updates_status):
        if childapi.option.isoptiondescription():
            props = set(childapi.property.get())
            obj = {}
            self.calc_raises_properties(obj, childapi)
            if props:
                lprops = list(props)
                lprops.sort()
                obj['properties'] = lprops
            try:
                self.config.option(path).option.get()
            except PropertiesOptionError:
                pass
        else:
            obj = self._gen_model_properties(childapi,
                                             path,
                                             None)
            if childapi.option.isfollower():
                for index in range(leader_len):
                    follower_childapi = self.config.unrestraint.option(path, index)
                    sobj = self._gen_model_properties(follower_childapi,
                                                      path,
                                                      index)
                    self._get_model_value(follower_childapi,
                                          path,
                                          sobj,
                                          index,
                                          updates_status)
                    if sobj:
                        model.setdefault(path, {})[str(index)] = sobj
            else:
                self._get_model_value(childapi,
                                      path,
                                      obj,
                                      None,
                                      updates_status)
        if obj:
            if not childapi.option.isoptiondescription() and childapi.option.isfollower():
                model.setdefault(path, {})['null'] = obj
            else:
                model[path] = obj

    def _get_model_value(self,
                         childapi,
                         path,
                         obj,
                         index,
                         updates_status):
        if path in updates_status and index in updates_status[path]:
            value = childapi.value.get()
            self._get_value_with_exception(obj,
                                           childapi,
                                           updates_status[path][index])
            del updates_status[path][index]
        else:
            try:
                with warnings.catch_warnings(record=True) as warns:
                    value = self.config.option(path, index=index).value.get()
                self._get_value_with_exception(obj,
                                               childapi,
                                               warns)
            except ValueError as err:
                self._get_value_with_exception(obj,
                                               childapi,
                                               [err])
                value = self.config.unrestraint.option(path, index=index).value.get()
            except PropertiesOptionError as err:
                config_bag = self.config._config_bag
                settings = config_bag.context.cfgimpl_get_settings()
                if settings._calc_raises_properties(config_bag.properties,
                                                    config_bag.permissives,
                                                    set(err.proptype)):
                    obj['hidden'] = True
                obj['display'] = False
                value = childapi.value.get()
        if value is not None and value != []:
            obj['value'] = value
        if not childapi.owner.isdefault():
            obj['owner'] = childapi.owner.get()

    def _get_value_with_exception(self,
                                  obj,
                                  childapi,
                                  values):
        for value in values:
            if isinstance(value, ValueError):
                obj.setdefault('error', [])
                msg = str(value)
                if msg not in obj.get('error', []):
                    obj['error'].append(msg)
                    obj['invalid'] = True
            elif isinstance(value.message, ValueErrorWarning):
                value.message.prefix = ''
                obj.setdefault('error', [])
                msg = str(value.message)
                if msg not in obj.get('error', []):
                    obj['error'].append(msg)
                    obj['invalid'] = True
            else:
                value.message.prefix = ''
                obj.setdefault('warnings', [])
                msg = str(value.message)
                if msg not in obj.get('error', []):
                    obj['warnings'].append(msg)
                    obj['hasWarnings'] = True

    def gen_global(self):
        ret = {}
        ret['owner'] = self.config.owner.get()
        ret['properties'] = list(self.config.property.get())
        ret['properties'].sort()
        ret['permissives'] = list(self.config.permissive.get())
        ret['permissives'].sort()
        return ret

    def get_form(self, form):
        ret = []
        buttons = []
        dict_form = {}
        for form_ in form:
            if 'key' in form_:
                dict_form[form_['key']] = form_
            elif form_.get('type') == 'submit':
                if 'cmd' not in form_:
                    form_['cmd'] = 'submit'
                buttons.append(form_)
            else:
                raise ValueError(_('unknown form {}').format(form_))

        for key, form_ in self.form.items():
            form_['key'] = key
            if key in dict_form:
                form_.update(dict_form[key])
            ret.append(form_)
        ret.extend(buttons)
        return ret

    def del_value(self, childapi, path, index):
        if index is not None and childapi.option.isleader():
            childapi.value.pop(index)
        elif index is None or childapi.option.isfollower():
            childapi.value.reset()
        else:
            multi = childapi.value.get()
            multi.pop(index)
            childapi.value.set(multi)

    def add_value(self, childapi, path, value):
        multi = childapi.value.get()
        multi.append(value)
        childapi.value.set(multi)

    def mod_value(self, childapi, path, index, value):
        if index is None or childapi.option.isfollower():
            childapi.value.set(value)
        else:
            multi = childapi.value.get()
            if len(multi) < index + 1:
                multi.append(value)
            else:
                multi[index] = value
            childapi.value.set(multi)

    def apply_updates(self,
                      oripath,
                      updates,
                      model_ori):
        updates_status = {}
        for update in updates:
            path = update['name']
            index = update.get('index')
            if oripath is not None and not path.startswith(oripath):
                raise ValueError(_('not in current area'))
            childapi = self.config.option(path)
            childapi_option = childapi.option
            if childapi_option.isfollower():
                childapi = self.config.option(path, index)
            with warnings.catch_warnings(record=True) as warns:
                try:
                    if update['action'] == 'modify':
                        self.mod_value(childapi,
                                       path,
                                       index,
                                       update.get('value', undefined))
                    elif update['action'] == 'delete':
                        self.del_value(childapi,
                                       path,
                                       index)
                    elif update['action'] == 'add':
                        if childapi_option.ismulti():
                            self.add_value(childapi, path, update['value'])
                        else:
                            raise ValueError(_('only multi option can have action "add", but "{}" is not a multi').format(path))
                    else:
                        raise ValueError(_('unknown action'))
                except ValueError as err:
                    updates_status.setdefault(path, {})[index] = [err]
            if warns != []:
                updates_status.setdefault(path, {}).setdefault(index, []).extend(warns)
        return updates_status

    def set_updates(self,
                    body):
        root_path = self.root
        updates = body.get('updates', [])
        updates_status = self.apply_updates(root_path,
                                            updates,
                                            body.get('model'))
        if 'model' in body:
            order = []
            old_model = body['model']
            new_model = self.todict(order=order,
                                    build_schema=False,
                                    build_form=False,
                                    updates_status=updates_status)['model']
            values = {'updates': list_keys(old_model, new_model, order, updates_status),
                      'model': new_model}
        else:
            values = None
        return values

    def todict(self,
               custom_form=[],
               build_schema=True,
               build_model=True,
               build_form=True,
               order=None,
               updates_status={}):
        rootpath = self.root
        if build_schema:
            schema = {}
        else:
            schema = None
        if build_model:
            model = {}
        else:
            model = None
        if build_form:
            form = {}
            buttons = []
        else:
            form = None
        self.walk(rootpath,
                  None,
                  schema,
                  model,
                  form,
                  order,
                  updates_status,
                  init=True)
        if build_form:
            for form_ in custom_form:
                if 'key' in form_:
                    key = form_.pop('key')
                    form.setdefault(key, {}).update(form_)
                elif form_.get('type') == 'submit':
                    # FIXME if an Option has a key "null"?
                    form.setdefault(None, []).append(form_)
                else:
                    raise ValueError(_('unknown form {}').format(form_))
        ret = {}
        if build_schema:
            ret['schema'] = schema
        if build_model:
            ret['model'] = model
            ret['global'] = self.gen_global()
        if build_form:
            ret['form'] = form
        ret['version'] = '1.0'
        return ret


def list_keys(model_a, model_b, ordered_key, updates_status):
    model_a_dict = {}
    model_b_dict = {}

    keys_a = set(model_a.keys())
    keys_b = set(model_b.keys())

    keys = (keys_a ^ keys_b) | set(updates_status.keys())

    for key in keys_a & keys_b:
        keys_mod_a = set(model_a[key].keys())
        keys_mod_b = set(model_b[key].keys())
        if keys_mod_a != keys_mod_b:
            keys.add(key)
        else:
            for skey in keys_mod_a:
                if model_a[key][skey] != model_b[key][skey]:
                    keys.add(key)
                    break
    def sort_key(key):
        try:
            return ordered_key.index(key)
        except ValueError:
            return -1
    return sorted(list(keys), key=sort_key)
