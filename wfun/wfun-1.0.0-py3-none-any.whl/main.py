from invoke import Program, Collection
from fun import tasks

program = Program(namespace=Collection.from_module(tasks), version='1.0.0')
