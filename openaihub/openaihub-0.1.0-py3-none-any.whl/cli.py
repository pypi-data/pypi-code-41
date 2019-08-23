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
@click.option("--path", metavar="NAME", required=True,
              help="")
@click.option("--operator", metavar="NAME", required=True,
              help="")
@click.option("--logpath", metavar="NAME", default='',
              help="")
@click.option("--version", "-v", metavar="VERSION",
              help="")
def register(path, operator, logpath, version):
    if logpath == '':
        logpath = path
    func.register(path, operator, logpath, version)
    
@cli.command()
@click.option("--namespace", "-e", metavar="NAME", default="operators",
              help="")
@click.option("--storage", "-s", metavar="NAME", default="",
              help="")
@click.option("--version", "-v", metavar="VERSION",
              help="")
def install(namespace, storage, version):
    func.install(namespace, storage, version)
