# Copyright (C) 2018-2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import Union, List, Dict, Tuple, Optional, Any
from argparse import ArgumentParser, Namespace, SUPPRESS, _HelpAction, HelpFormatter
from copy import copy
from gettext import gettext as _

try:
    from tiramisu import Config
    from tiramisu.error import PropertiesOptionError, RequirementError, LeadershipError
except ImportError:
    Config = None
    from tiramisu_api.error import PropertiesOptionError
    RequirementError = PropertiesOptionError
    LeadershipError = ValueError
try:
    from tiramisu__api import Config as ConfigJson
    if Config is None:
        Config = ConfigJson
except ImportError:
    ConfigJson = Config


def get_choice_list(obj, properties, display):
    def convert(choice):
        if isinstance(choice, int):
            return str(choice)
        return choice
    choices = [convert(choice) for choice in obj.value.list()]
    if choices[0] == '':
        del choices[0]
    if display:
        choices = '{{{}}}'.format(','.join(choices))
        if 'mandatory' not in properties:
            choices = '[{}]'.format(choices)
    return choices


class TiramisuNamespace(Namespace):
    def __init__(self,
                 config: Config,
                 root: Optional[str]) -> None:
        super().__setattr__('_config', config)
        super().__setattr__('_root', root)
        super().__setattr__('list_force_no', {})
        super().__setattr__('list_force_del', {})
        super().__setattr__('arguments', {})
        self._populate()
        super().__init__()

    def _populate(self) -> None:
        if self._root is None:
            config = self._config
        else:
            config = self._config.option(self._root)
        for tiramisu_key, tiramisu_value in config.value.dict(fullpath=True).items():
            option = self._config.option(tiramisu_key)
            if not option.option.issymlinkoption():
                if tiramisu_value == [] and \
                        option.option.ismulti():  # and \
                        # option.owner.isdefault():
                    tiramisu_value = None
                super().__setattr__(tiramisu_key, tiramisu_value)

    def __setattr__(self,
                    key: str,
                    value: Any) -> None:
        if key in self.list_force_no:
            true_key = self.list_force_no[key]
        elif key in self.list_force_del:
            true_key = self.list_force_del[key]
        else:
            true_key = key
        option = self._config.option(true_key)
        if option.option.isfollower():
            _setattr = self._setattr_follower
            true_value = ','.join(value[1:])
        else:
            _setattr = self._setattr
            true_value = value
        if option.option.type() == 'choice':
            # HACK if integer in choice
            values = option.value.list()
            if isinstance(value, list):
                int_value = []
                for val in value:
                    if isinstance(val, str) and val.isdigit():
                        int_val = int(val)
                        if int_val in values:
                            val = int_val
                    int_value.append(val)
                value = int_value
            elif value not in values and isinstance(value, str) and value.isdigit():
                int_value = int(value)
                if int_value in values:
                    value = int_value
        try:
            if key in self.list_force_del:
                option.value.pop(value)
            else:
                _setattr(option, true_key, key, value)
        except ValueError as err:
            if option.option.type() == 'choice':
                values = option.value.list()
                if isinstance(true_value, list):
                    for val in value:
                        if val not in values:
                            display_value = val
                            break
                else:
                    display_value = true_value
                choices = get_choice_list(option, option.property.get(), False)
                raise ValueError("argument {}: invalid choice: '{}' (choose from {})".format(self.arguments[key], display_value, ', '.join([f"'{val}'" for val in choices])))
            else:
                raise err

    def _setattr(self,
                 option: 'Option',
                 true_key: str,
                 key: str,
                 value: Any) -> None:
        if option.option.ismulti() and \
                value is not None and \
                not isinstance(value, list):
            value = [value]
        option.value.set(value)

    def _setattr_follower(self,
                          option: 'Option',
                          true_key: str,
                          key: str,
                          value: Any) -> None:
        if not value[0].isdecimal():
            raise ValueError('index must be a number, not {}'.format(value[0]))
        index = int(value[0])
        if option.option.type() == 'boolean':
            value = key not in self.list_force_no
        elif option.option.issubmulti():
            value = value[1:]
        else:
            value = value[1]
        self._config.option(true_key, index).value.set(value)


class TiramisuHelpFormatter:
    def _get_default_metavar_for_optional(self,
                                          action):
        ret = super()._get_default_metavar_for_optional(action)
        if '.' in ret:
            ret = ret.rsplit('.', 1)[1]
        return ret

    class _Section(HelpFormatter._Section):
        def format_help(self):
            # Remove empty OD
            if self.formatter.remove_empty_od and \
                    len(self.items) == 1 and \
                    self.items[0][0].__name__ == '_format_text':
                return ''
            return super().format_help()


class _TiramisuHelpAction(_HelpAction):
    needs = False
    def __call__(self, *args, **kwargs):
        _TiramisuHelpAction.needs = True

    def display(self, parser):
        _HelpAction.__call__(self, parser, None, None)


class _BuildKwargs:
    def __init__(self,
                 name: str,
                 option: 'Option',
                 cmdlineparser: 'TiramisuCmdlineParser',
                 properties: List[str],
                 force_no: bool,
                 force_del: bool,
                 display_modified_value: bool,
                 not_display: bool) -> None:
        self.kwargs = {}
        self.cmdlineparser = cmdlineparser
        self.properties = properties
        self.force_no = force_no
        self.force_del = force_del
        if (not self.force_no or (not_display and not display_modified_value)) and not self.force_del:
            description = option.doc()
            if not description:
                description = description.replace('%', '%%')
            self.kwargs['help'] = description
        if 'positional' not in self.properties:
            is_short_name = self.cmdlineparser._is_short_name(name, 'longargument' in self.properties)
            if self.force_no:
                ga_name = self.gen_argument_name(name, is_short_name)
                ga_path = self.gen_argument_name(option.path(), is_short_name)
                self.cmdlineparser.namespace.list_force_no[ga_path] = option.path()
            elif self.force_del:
                ga_name = self.gen_argument_name(name, is_short_name)
                ga_path = self.gen_argument_name(option.path(), is_short_name)
                self.cmdlineparser.namespace.list_force_del[ga_path] = option.path()
            else:
                ga_name = name
            self.kwargs['dest'] = self.gen_argument_name(option.path(), False)
            argument = self.cmdlineparser._gen_argument(ga_name, is_short_name)
            self.cmdlineparser.namespace.arguments[option.path()] = argument
            self.args = [argument]
        else:
            self.cmdlineparser.namespace.arguments[option.path()] = option.path()
            self.args = [option.path()]

    def __setitem__(self,
                    key: str,
                    value: Any) -> None:
        self.kwargs[key] = value

    def add_argument(self,
                     option: 'Option'):
        is_short_name = self.cmdlineparser._is_short_name(option.name(), 'longargument' in self.properties)
        if self.force_no:
            name = self.gen_argument_name(option.name(), is_short_name)
        elif self.force_del:
            name = self.gen_argument_name(option.name(), is_short_name)
        else:
            name = option.name()
        argument = self.cmdlineparser._gen_argument(name, is_short_name)
        self.cmdlineparser.namespace.arguments[option.path()] = argument
        self.args.insert(0, argument)

    def gen_argument_name(self, name, is_short_name):
        if self.force_no:
            if is_short_name:
                prefix = 'n'
            else:
                prefix = 'no-'
            if '.' in name:
                sname = name.rsplit('.', 1)
                name = sname[0] + '.' + prefix + sname[1]
            else:
                name = prefix + name
        if self.force_del:
            if is_short_name:
                prefix = 'p'
            else:
                prefix = 'pop-'
            if '.' in name:
                sname = name.rsplit('.', 1)
                name = sname[0] + '.' + prefix + sname[1]
            else:
                name = prefix + name
        return name

    def get(self) -> Tuple[Dict]:
        return self.args, self.kwargs


class TiramisuCmdlineParser(ArgumentParser):
    def __init__(self,
                 config: Union[Config, ConfigJson],
                 *args,
                 root: str=None,
                 fullpath: bool=True,
                 remove_empty_od: bool=False,
                 display_modified_value: bool=True,
                 formatter_class=HelpFormatter,
                 _forhelp: bool=False,
                 **kwargs):
        self.fullpath = fullpath
        self.config = config
        self.root = root
        self.remove_empty_od = remove_empty_od
        self.display_modified_value = display_modified_value
        if TiramisuHelpFormatter not in formatter_class.__mro__:
            formatter_class = type('TiramisuHelpFormatter', (TiramisuHelpFormatter, formatter_class), {})
        formatter_class.remove_empty_od = self.remove_empty_od
        kwargs['formatter_class'] = formatter_class
        if self.root is None:
            subconfig = self.config.option
        else:
            subconfig = self.config.option(self.root)
        self.namespace = TiramisuNamespace(self.config, self.root)
        super().__init__(*args, **kwargs)
        self.register('action', 'help', _TiramisuHelpAction)
        self._config_to_argparser(_forhelp,
                                  subconfig,
                                  self.root)

    def _pop_action_class(self, kwargs, default=None):
        ret = super()._pop_action_class(kwargs, default)
        if kwargs.get('action') != 'help' and kwargs.get('dest') != 'help':
            return ret
        return _TiramisuHelpAction

    def _match_arguments_partial(self,
                                 actions,
                                 arg_string_pattern):
        # used only when check first proposal for first value
        # we have to remove all actions with propertieserror
        # so only first settable option will be returned
        actions_pop = []
        for idx, action in enumerate(actions):
            if self.config.option(action.dest).property.get(only_raises=True):
                actions_pop.append(idx)
            else:
                break
        for idx in actions_pop:
            actions.pop(0)
        return super()._match_arguments_partial(actions, arg_string_pattern)

    def _is_short_name(self, name, longargument):
        return len(name) == 1 and not longargument

    def _gen_argument(self, name, is_short_name):
        if is_short_name:
            return self.prefix_chars + name
        return self.prefix_chars * 2 + name

    def _parse_known_args(self, args=None, namespace=None):
        try:
            namespace_, args_ = super()._parse_known_args(args, namespace)
        except (ValueError, LeadershipError) as err:
            self.error(err)
        if args != args_ and args_ and args_[0].startswith(self.prefix_chars):
            # option that was disabled are no more disable
            # so create a new parser
            new_parser = TiramisuCmdlineParser(self.config,
                                               self.prog,
                                               root=self.root,
                                               remove_empty_od=self.remove_empty_od,
                                               display_modified_value=self.display_modified_value,
                                               formatter_class=self.formatter_class,
                                               epilog=self.epilog,
                                               description=self.description,
                                               fullpath=self.fullpath)
            namespace_, args_ = new_parser._parse_known_args(args_, new_parser.namespace)
        else:
            if self._registries['action']['help'].needs:
                # display help only when all variables assignemnt are done
                self._registries['action']['help'].needs = False
                helper = self._registries['action']['help'](None)
                helper.display(self)
        return namespace_, args_

    def add_argument(self, *args, **kwargs):
        if args == ('-h', '--help'):
            super().add_argument(*args, **kwargs)
        else:
            raise NotImplementedError(_('do not use add_argument'))

    def add_arguments(self, *args, **kwargs):
        raise NotImplementedError(_('do not use add_argument'))

    def add_subparsers(self, *args, **kwargs):
        raise NotImplementedError(_('do not use add_subparsers'))

    def _option_is_not_default(self,
                               properties,
                               type,
                               name,
                               value):
        if 'positional' not in properties:
            is_short_name = self._is_short_name(name, 'longargument' in properties)
            self.prog += ' {}'.format(self._gen_argument(name, is_short_name))
        if type != 'boolean':
            if isinstance(value, list):
                for val in value:
                    self.prog += ' "{}"'.format(val)
            else:
                self.prog += ' "{}"'.format(value)

    def _config_list(self,
                     config: Config,
                     prefix: Optional[str],
                     _forhelp: bool,
                     group, level):
        for obj in config.list(type='all'):
            # do not display frozen option
            if 'frozen' in obj.option.properties():
                continue
            if obj.option.isoptiondescription():
                if _forhelp:
                    newgroup = self.add_argument_group(obj.option.path(), obj.option.description())
                else:
                    newgroup = group
                if prefix:
                    prefix_ = prefix + '.' + obj.option.name()
                else:
                    prefix_ = obj.option.path()
                self._config_to_argparser(_forhelp, obj, prefix_, newgroup, level + 1)
            elif obj.option.type() == 'boolean' and not obj.option.issymlinkoption():
                if not obj.option.isleader():
                    yield obj, False, None
                    yield obj, True, None
                else:
                    yield obj, False, False
                    yield obj, False, True
                    yield obj, True, None
            elif obj.option.isleader():
                yield obj, None, False
                yield obj, None, True
            else:
                yield obj, None, None

    def _config_to_argparser(self,
                             _forhelp: bool,
                             config,
                             prefix: Optional[str],
                             group=None,
                             level=0) -> None:
        if group is None:
            group = super()
        actions = {}
        leadership_len = None
        options_is_not_default = {}
        for obj, force_no, force_del in self._config_list(config, prefix, _forhelp, group, level):
            option = obj.option
            name = option.name()
            if name.startswith(self.prefix_chars):
                raise ValueError(_('name cannot startswith "{}"').format(self.prefix_chars))
            if option.issymlinkoption():
                symlink_name = option.name(follow_symlink=True)
                if symlink_name in options_is_not_default:
                    options_is_not_default[symlink_name]['name'] = name
                if symlink_name in actions:
                    for action in actions[symlink_name]:
                        action.add_argument(option)
                continue
            if force_del:
                value = None
            elif option.isleader():
                value = obj.value.get()
                leadership_len = len(value)
            elif option.isfollower():
                value = []
                for index in range(leadership_len):
                    value.append(self.config.option(obj.option.path(), index).value.get())
            else:
                value = obj.value.get()
            if self.fullpath and prefix:
                name = prefix + '.' + name
            if option.isfollower():
                properties = obj.option.properties()
            else:
                properties = obj.property.get()
            not_display = not option.isfollower() and not obj.owner.isdefault() and value is not None
            kwargs = _BuildKwargs(name, option, self, properties, force_no, force_del, self.display_modified_value, not_display)
            if _forhelp and not_display and ((value is not False and not force_no) or (value is False and force_no)):
                options_is_not_default[option.name()] = {'properties': properties,
                                                         'type': option.type(),
                                                         'name': name,
                                                         'value': value}
                if not self.display_modified_value:
                    continue
            if 'positional' in properties:
                if option.type() == 'boolean':
                    raise ValueError(_('boolean option must not be positional'))
                if not 'mandatory' in properties:
                    raise ValueError('"positional" argument must be "mandatory" too')
                if _forhelp:
                    kwargs['default'] = obj.value.default()
                else:
                    kwargs['default'] = value
                    kwargs['nargs'] = '?'
            else:
                kwargs['default'] = SUPPRESS
                if _forhelp and 'mandatory' in properties:
                    kwargs['required'] = True
                if not force_del and option.type() == 'boolean':
                    if not option.isfollower():
                        if 'storefalse' in properties:
                            if force_no:
                                action = 'store_true'
                            else:
                                action = 'store_false'
                        elif force_no:
                            action = 'store_false'
                        else:
                            action = 'store_true'
                        kwargs['action'] = action
                    else:
                        kwargs['metavar'] = 'INDEX'
            if option.type() != 'boolean' or force_del:
                if not force_del:
                    if _forhelp:
                        value = obj.value.default()
                    if value not in [None, []]:
                        #kwargs['default'] = kwargs['const'] = option.default()
                        #kwargs['action'] = 'store_const'
                        kwargs['nargs'] = '?'

                    if not option.isfollower() and option.ismulti():
                        if _forhelp and 'mandatory' in properties:
                            kwargs['nargs'] = '+'
                        else:
                            kwargs['nargs'] = '*'
                if option.isfollower() and not option.type() == 'boolean':
                    metavar = option.name().upper()
                    if option.issubmulti():
                        kwargs['nargs'] = '+'
                    else:
                        kwargs['nargs'] = 2
                        if _forhelp and 'mandatory' not in properties:
                            metavar = '[{}]'.format(metavar)
                    if option.type() == 'choice':
                        # do not manage choice with argparse there is problem with integer problem
                        kwargs['metavar'] = ('INDEX', get_choice_list(obj, properties, True))
                    else:
                        kwargs['metavar'] = ('INDEX', metavar)
                if force_del:
                    kwargs['metavar'] = 'INDEX'
                    kwargs['type'] = int
                elif option.type() == 'string':
                    pass
                elif option.type() == 'integer' or option.type() == 'boolean':
                    # when boolean we are here only if follower
                    kwargs['type'] = int
                    if _forhelp and option.type() == 'boolean':
                        kwargs['metavar'] = 'INDEX'
                        kwargs['nargs'] = 1
                elif option.type() == 'choice' and not option.isfollower():
                    # do not manage choice with argparse there is problem with integer problem
                    kwargs['choices'] = get_choice_list(obj, properties, False)
                else:
                    pass
            actions.setdefault(option.name(), []).append(kwargs)
        for option_is_not_default in options_is_not_default.values():
            self._option_is_not_default(**option_is_not_default)
        for values in actions.values():
            for value in values:
                args, kwargs = value.get()
                group.add_argument(*args, **kwargs)
    def _valid_mandatory(self):
        pass

    def parse_args(self,
                   *args,
                   valid_mandatory=True,
                   **kwargs):
        kwargs['namespace'] = self.namespace
        try:
            namespaces = super().parse_args(*args, **kwargs)
        except PropertiesOptionError as err:
            name = err._option_bag.option.impl_getname()
            properties = self.config.option(name).property.get()
            if self.fullpath and 'positional' not in properties:
                if len(name) == 1 and 'longargument' not in properties:
                    name = self.prefix_chars + name
                else:
                    name = self.prefix_chars * 2 + name
            if err.proptype == ['mandatory']:
                self.error('the following arguments are required: {}'.format(name))
            else:
                self.error('unrecognized arguments: {}'.format(name))
        if valid_mandatory:
            errors = []
            for key in self.config.value.mandatory():
                properties = self.config.option(key).option.properties()
                if not self.config.option(key).option.isfollower():
                    if 'positional' not in properties:
                        if self.fullpath or '.' not in key:
                            name = key
                        else:
                            name = key.rsplit('.', 1)[1]
                        is_short_name = self._is_short_name(name, 'longargument' in self.config.option(key).property.get())
                        args = self._gen_argument(name, is_short_name)
                    else:
                        args = key
                else:
                    if 'positional' not in properties:
                        args = self._gen_argument(key, False)
                    else:
                        args = key
                if not self.fullpath and '.' in args:
                    args = args.rsplit('.', 1)[1]
                    if 'positional' not in properties:
                        args = self._gen_argument(args, False)
                errors.append(args)
            if errors:
                self.error('the following arguments are required: {}'.format(', '.join(errors)))
        return namespaces

    def format_usage(self,
                     *args,
                     **kwargs):
        help_formatter = TiramisuCmdlineParser(self.config,
                                               self.prog,
                                               root=self.root,
                                               fullpath=self.fullpath,
                                               remove_empty_od=self.remove_empty_od,
                                               display_modified_value=self.display_modified_value,
                                               formatter_class=self.formatter_class,
                                               epilog=self.epilog,
                                               description=self.description,
                                               _forhelp=True)
        return super(TiramisuCmdlineParser, help_formatter).format_usage(*args, **kwargs)

    def format_help(self):
        help_formatter = TiramisuCmdlineParser(self.config,
                                               self.prog,
                                               root=self.root,
                                               fullpath=self.fullpath,
                                               remove_empty_od=self.remove_empty_od,
                                               display_modified_value=self.display_modified_value,
                                               formatter_class=self.formatter_class,
                                               epilog=self.epilog,
                                               description=self.description,
                                               _forhelp=True)
        return super(TiramisuCmdlineParser, help_formatter).format_help()

    def get_config(self):
        return self.config
