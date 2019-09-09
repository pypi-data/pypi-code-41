# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
import os
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template/apigw")
Variable = namedtuple('Variable', ['key', 'value'])


class Block:

    def __init__(self):
        self.sets = []

    def set_var(self, key, value):
        self.sets.append(Variable(key, value))

    def load(self):
        pass

    def dump(self, template_name, render_key_pairs):
        j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR),
                             trim_blocks=True)
        return j2_env.get_template(template_name).render(render_key_pairs)

    def append(self, block):
        raise NotImplementedError

    def remove(self):
        pass
