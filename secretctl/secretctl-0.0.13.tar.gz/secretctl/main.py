"""main.py"""
from invoke import Collection, Program
import pkg_resources
from secretctl import cli

#program = Program(namespace=Collection.from_module(cli), version=get_version(root='..', relative_to=__file__))
program = Program(namespace=Collection.from_module(cli), version=pkg_resources.get_distribution('secretctl').version)
