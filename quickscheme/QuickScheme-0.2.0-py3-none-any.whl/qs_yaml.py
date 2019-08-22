'''
Ordered Yaml Load/Dump and other YAML Utilities
'''

from collections import OrderedDict

import yaml


class UnsortableList(list):
    ''' Unsortable List'''

    def sort(self, *_args, **_kwargs):
        ''' Sort Override '''
        print("DOnt sort me, bro!")
        # pass


class UnsortableOrderedDict(OrderedDict):
    ''' Unsortable Ordered Dict '''

    def items(self, *args, **kwargs):
        ''' List items in dictionary '''
        return UnsortableList(OrderedDict.items(self, *args, **kwargs))


yaml.add_representer(UnsortableOrderedDict,
                     yaml.representer.SafeRepresenter.represent_dict)
yaml.SafeDumper.add_representer(UnsortableOrderedDict,
                                yaml.representer.SafeRepresenter.represent_dict)
yaml.add_representer(UnsortableList,
                     yaml.representer.SafeRepresenter.represent_dict)
yaml.SafeDumper.add_representer(UnsortableList,
                                yaml.representer.SafeRepresenter.represent_dict)


def load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    ''' yaml.load proxy '''
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def safe_load(stream, object_pairs_hook=OrderedDict):
    ''' Safe Load '''
    return load(stream, yaml.SafeLoader, object_pairs_hook)


def dump(data, stream=None, Dumper=yaml.Dumper, **kwargs):
    ''' yaml.dump proxy '''

    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    OrderedDumper.add_representer(UnsortableOrderedDict,
                                  yaml.representer.SafeRepresenter.represent_dict)
    OrderedDumper.add_representer(UnsortableList,
                                  yaml.representer.SafeRepresenter.represent_dict)

    return yaml.dump(data, stream, OrderedDumper, **kwargs)


def safe_dump(data, stream=None, **kwargs):
    ''' Safe Dump '''
    return dump(data, stream, yaml.SafeDumper, **kwargs)


def pretty_dump(data, stream=None, **kwargs):
    ''' Pretty dump '''
    kwargs.update(dict(default_flow_style=False,
                       default_style='', sort_keys=False))
    return safe_dump(data, stream, **kwargs)
