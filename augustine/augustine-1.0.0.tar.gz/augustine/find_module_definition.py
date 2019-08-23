# coding=utf-8
from typing import Any, Sequence, TypeVar

from ._core import log


ModuleDefinition = TypeVar('ModuleDefinition')


def find_module_definition(specification):
    # type: (str) -> ModuleDefinition
    log.debug('Finding module definition from: ' + specification)
    if ':' not in specification:
        raise ValueError(
            'Module reference specification must be in the format of [package.]module:definition. '
            'Instead it is:' + specification)

    module_name, definition = specification.split(':')
    log.debug("Module name: {} - definition: {}".format(module_name, definition))

    if not module_name:
        raise ValueError('No module was found in the module definition specified by: ' + specification)

    if not definition:
        raise ValueError('No definition was found in the module definition specified by: ' + specification)

    _module = __import__(module_name, fromlist=definition)
    log.debug('Imported module: ' + repr(_module))

    return _get_definition(_module, definition.split('.'))


def _get_definition(_object, path):
    # type: (Any, Sequence[str]) -> ModuleDefinition
    log.debug("Searching for definition '{}' in {}...".format('.'.join(path), repr(_object)))

    definition_name = path[0]
    if not hasattr(_object, definition_name):
        raise "Unable to find definition '{}' in {}.".format(definition_name, repr(_object))

    definition = getattr(_object, definition_name)
    log.debug("Found definition '{}' in {}".format(definition_name, repr(_object)))

    remaining_paths = path[1:]
    if not remaining_paths:
        return definition

    log.debug('Remaining paths: ' + repr(remaining_paths))
    return _get_definition(definition, remaining_paths)
