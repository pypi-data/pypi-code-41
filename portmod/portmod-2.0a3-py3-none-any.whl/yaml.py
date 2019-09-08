# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""PyYAML wrapper to avoid breaking compatibility with older versions of PyYAML"""

import yaml


class Person(yaml.YAMLObject):
    yaml_tag = "!person"

    def __init__(self, name="", email="", desc=""):
        self.update(name, email, desc)

        if not name and not email:
            raise Exception("Cannot create empty Person")

    def update(self, name, email, desc):
        self.name = name
        self.email = email
        self.desc = desc

    def __repr__(self):
        return "{}(name={}, email={}, desc={})".format(
            self.__class__.__name__, self.name, self.email, self.desc
        )

    @staticmethod
    def from_yaml(loader, node):
        if isinstance(node, yaml.ScalarNode):
            return Person(node.value)
        else:
            node_map = loader.construct_mapping(node, deep=True)
            return Person(**node_map)


class Group(yaml.YAMLObject):
    yaml_tag = "!group"

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "%s(name=%r)" % (self.__class__.__name__, self.name)

    @staticmethod
    def from_yaml(loader, node):
        if isinstance(node, yaml.ScalarNode):
            return Group(node.value)
        else:
            node_map = loader.construct_mapping(node, deep=True)
            return Group(**node_map)


try:
    yaml.add_constructor("!person", Person.from_yaml, Loader=yaml.FullLoader)
    yaml.add_constructor("!group", Group.from_yaml, Loader=yaml.FullLoader)
except AttributeError:
    pass


def yaml_load(file):
    """
    Loads yaml file

    Attempt to use the safer yaml.full_load, but fall back to unsafe load
    to avoid breaking compatibility
    """
    try:
        return yaml.full_load(file)  # type: ignore
    except AttributeError:
        return yaml.load(file)  # type: ignore
