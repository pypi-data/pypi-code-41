# Copyright 2019 IBM Corporation 
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License. 
from __future__ import print_function
import logging
import sys
import os
# pylint: disable=wrong-import-position
import openaihub.func as func

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import click
from click import UsageError

@click.group()
@click.version_option()
def cli():
    pass

@cli.command()
@click.version_option(expose_value=False)
@click.option("--path", metavar="PATH", required=True,
              help="path to the operator manifest")
@click.option("--operator", metavar="NAME", required=True,
              help="operator name")
@click.option("--logpath", metavar="PATH", default='',
              help="logging path")
def register(path, operator, logpath):
    if logpath == '': logpath = path
    func.register(path, operator.lower(), logpath)
    
@cli.command()
@click.version_option(expose_value=False)
@click.option("--namespace", "-e", metavar="NAMESPACE", default="operators", show_default=True,
              help="namespace where the applications will be installed")
@click.option("--storage", "-s", metavar="NAME", default="", type=click.Choice(['nfs', '']), show_default=True,
              help="storageclass for pvcs")
def install(namespace, storage):
    func.install(namespace, storage)

@cli.command()
@click.version_option(expose_value=False)
@click.option("--operator", "-o", metavar="NAME", required=True,
              help="name of the operator to be installed")
@click.option("--subscription-file", "-f", metavar="FILE", default='', show_default=True,
              help="file (with path) of the subscription for the operator")
@click.option("--logpath", metavar="PATH", default='',
              help="logging path")
def install_operator(operator, subscription_file, logpath):
    if logpath == '': logpath = os.getcwd() 
    func.install_operator(operator.lower(), subscription_file, logpath)
