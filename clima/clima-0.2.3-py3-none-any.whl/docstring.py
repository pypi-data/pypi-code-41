"""Doc string handling"""
from collections import OrderedDict
import inspect


def wrap_method_docstring(cls: object, nt):
    """
    In Place util function that prepares the docstrings of the given class
    so that it includes the parameters and details from given object `nt`

    Returns:
        None
    """
    methods = [m.object for m in inspect.classify_class_attrs(cls)
               if m.kind == 'method' and not m.name.startswith('_')]
    for m in methods:
        args = prepare_docstring_help(nt)
        replace_docstring(m, args)


def replace_docstring(func, args):
    docstring = func.__doc__
    docstring = (docstring if docstring is not None else '') + '\nArgs:\n' + args
    func.__doc__ = docstring


def attr_map(parsed_params):
    """Mapping for the schema's fields (parameters)"""
    mapped_attrs = {}
    for param_type, def_desc in parsed_params.items():
        if ':' in param_type:
            param, _type = param_type.split(':', 1)
            _type = _type.strip()
        else:
            param = param_type
            _type = None

        # TODO: this won't handle # in strings ...
        if '#' in def_desc:
            default, description = def_desc.split('#', 1)
            default = default.strip()
            description = description.strip()
        else:
            default = def_desc.strip()
            description = ''

        mapped_attrs.update(
            {
                param: {
                    'type': _type,
                    'default': default,
                    'description': description,
                }
            }
        )
    return mapped_attrs


def parse_source_for_params(params):
    """
    parse the source of the schema and split its
    fields
    """
    split_parameters = {
        tuple(
            str(argtype_and_defdesc).strip()
            for argtype_and_defdesc in src_line.split('=', 1)
        )
        for src_line in params
        if src_line.startswith(' ')
    }
    return OrderedDict(split_parameters)


def argument_help(attr_name, attr):
    _type = attr['type'] if attr['type'] is not None else ""
    fmt = '    --{} ({}): {} (Default is {})'
    return fmt.format(attr_name, _type, attr['description'], attr['default'])


def filter_params(N):
    """Filter source lines of the class
    Returns:
        fields as source lines
    """
    filtered_source = []
    for line in inspect.getsourcelines(N.__class__)[0][1:]:
        # When parsing, post_init would bleed into the attributes without this hack
        if line.strip().startswith('def '):
            break
        filtered_source.append(line)
    return filtered_source


def prepare_docstring_help(N):
    """Replace docstrings to include the parameters (schema)"""

    args = []
    if hasattr(N, '__annotations__'):
        for attr_name, cls in N.__annotations__.items():

            filtered = filter_params(N)
            parsed = parse_source_for_params(filtered)
            attr = attr_map(parsed).get(attr_name)
            if attr is None:
                continue

            args.append(argument_help(attr_name, attr))

    return '\n'.join(args)
