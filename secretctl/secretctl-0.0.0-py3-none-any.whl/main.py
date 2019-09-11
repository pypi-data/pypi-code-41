"""main.py"""
import pkg_resources
from invoke import Collection, Program
from secretctl import cli

program = Program(namespace=Collection.from_module(cli), version=pkg_resources.get_distribution("secretctl").version)
#program = Program(namespace=Collection.from_module(cli), version='0.0.15')
