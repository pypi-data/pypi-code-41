#!/usr/bin/env python

# Copyright (c) 2016 aos Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import os, sys
import json
import click

from aos.util import *
from aos.repo import *
from aos.managers.comp import CompManager
import ConfigParser

@click.group(short_help="Component Manager")
@click.pass_context
def cli(ctx):
    ctx.obj = CompManager()

#
# Functions
#
def print_component_status(json_format):
    cwd_type = Repo().pathtype()
    os_name = OS_NAME

    if cwd_type == 'program':
        pd = Program(os.getcwd())
        aos_path = pd.get_cfg(OS_PATH)
        aos_remote_components = get_aos_components(pd.get_cfg(REMOTE_PATH))
        os_name = 'aos'
    else:
        if os.path.isdir("kernel/rhino"):
            aos_path = os.getcwd()
        else:
            aos_path = Global().get_cfg(AOS_SDK_PATH)

    aos_local_components = get_aos_components(aos_path)
    if json_format:
        json_components_dict = {}

        if cwd_type == 'program':
            pd = Program(os.getcwd())
            with cd(pd.get_cfg(PROGRAM_PATH)):
                cube_add_components = None
                cube_remove_components = None
                with open(CUBE_MAKEFILE, 'r') as fin:
                    for line in fin:
                        if line.startswith('CUBE_ADD_COMPONENTS :='):
                            cube_add_components = re.split('\s+', line[23:].strip())

                        if line.startswith('CUBE_REMOVE_COMPONENTS :='):
                            cube_remove_components = re.split('\s+', line[26:].strip())

                for path, name in aos_remote_components.items():
                    cube_add = False
                    cube_remove = False

                    rel_path = os.path.dirname(relpath(pd.get_cfg(PROGRAM_PATH), path))
                    if cube_add_components and os.path.dirname(rel_path) in cube_add_components:
                        cube_add = True
                    if cube_remove_components and os.path.dirname(rel_path) in cube_remove_components:
                        cube_remove = True

                    json_components_dict[rel_path] = {'name': name, 'cube_add': cube_add, 'cube_remove': cube_remove}

                for path, name in aos_local_components.items():
                    cube_add = False
                    cube_remove = False

                    rel_aos_path = os.path.dirname(relpath(aos_path, path))
                    rel_path = os.path.join(os_name, rel_aos_path).replace(os.path.sep, '/')

                    if cube_add_components and rel_aos_path in cube_add_components:
                        cube_add = True
                    if cube_remove_components and rel_aos_path in cube_remove_components:
                        cube_remove = True

                    json_components_dict[rel_path] = {'name': name, 'cube_add': cube_add, 'cube_remove': cube_remove}
        else:
            cube_add = False
            cube_remove = False
            for path, name in aos_local_components.items():
                json_components_dict[os.path.dirname(relpath(os.path.dirname(aos_path), path))] = {'name': name, 'cube_add': cube_add, 'cube_remove': cube_remove}

        print(json.dumps(json_components_dict, indent=4, sort_keys=True))
    else:
        if cwd_type != 'program':
            print('\nCurrent directory isn\'t AliOS-Things program, list AOS_SDK_PATH components.')
        print("\n                                                      AliOS-Things COMPONENTS                ")
        print('|===================================================================================================================|')

        print('| %-30s | %-80s |' % ('NAME', 'LOCATION'))

        if cwd_type == 'program':
            program_path = Program(os.getcwd()).get_cfg(PROGRAM_PATH)
            for path, name in aos_remote_components.items():
                print('| %-30s | %-80s |' % (name, os.path.dirname(relpath(program_path, path))))
        for path, name in aos_local_components.items():
            print('| %-30s | %-80s |' % (name, os.path.dirname(relpath(os.path.dirname(aos_path), path))))

        print('|===================================================================================================================|')

def get_aos_components(aos_path):
    makefile_dict = {}
    if os.path.isdir(aos_path):
        for (dir_path, dir_names, file_names) in os.walk(aos_path):
            for f in file_names:
                if ('out' not in dir_path) and ('build' not in dir_path) and ('tools/codesync' not in dir_path) and f.endswith('.mk'):
                    makefile_dict[os.path.join(dir_path, f)] = f[:-3]
    else:
        error('Find components dir is empty!')

    aos_components_dict = {}
    for path, name in makefile_dict.items():
        with open(path, 'r') as f:
            s = f.read()
            component_name = re.findall('^\s*NAME\s*:?=\s*(\S+)\s*\n', s)
            if len(component_name) == 1:
                aos_components_dict[path.replace(os.path.sep, '/')] = component_name[0]

    return aos_components_dict

# List command
@cli.command("list", short_help="List installed components")
@click.argument("components", required=False, nargs=-1, metavar="[COMPONENTS...]")
@click.option("--json-output", is_flag=True)
@click.option("-r", "--remote", is_flag=True, help="List remote components")
@click.option("-d", "--showduplicates", is_flag=True, help="show all versions of components")
@click.pass_obj
def list_component(cm, components, json_output, remote, showduplicates):
    #print_component_status(json_output)
    args = []
    if showduplicates:
        args += ["--showduplicates"]

    if components:
        args += components

    # Clean cached data first
    cm.clean()
    output, err = cm.list(remote, *args)
    click.echo(output)

# Install command
@cli.command("install", short_help="Install components")
@click.argument("components", required=True, nargs=-1, metavar="[COMPONENTS...]")
@click.option("-t", "--check-available", is_flag=True, help="Check if component available before installation")
#@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
#@click.option("--interactive", is_flag=True, help="Allow to make a choice for all prompts")
@click.pass_obj
def install_component(cm, components, check_available):
    cm.install(components, check_available)
    os.chdir(os.path.join(cm.project_dir, OS_NAME))
    update_config_in()

# Uninstall command
@cli.command("uninstall", short_help="Uninstall components")
@click.argument("components", required=False, nargs=-1, metavar="[COMPONENTS...]")
@click.option("-a", "--all", is_flag=True, help="Uninstall all components")
@click.option("-f", "--force", is_flag=True, help="Force to uninstall components")
@click.pass_obj
def uninstall_component(cm, components, all, force):
    if all:
        complist = []
        output, err = cm.list(remote=None)
        patten = re.compile(r"(.*\.noarch)\s*(.*)aos\s*installed")
        for line in output.splitlines():
            match = patten.match(line)
            if match:
                complist += [match.group(1)]

        if complist:
            components = complist

    opts = []
    if force:
        opts += ["--nodeps"]

    cm.uninstall(components, *opts)
    os.chdir(os.path.join(cm.project_dir, OS_NAME))
    update_config_in()

# Update command
@cli.command("update", short_help="Update installed components")
@click.argument("components", required=False, nargs=-1, metavar="[COMPONENTS...]")
@click.option("-c", "--only-check", is_flag=True, help="Do not update, only check for new version")
@click.option("--json-output", is_flag=True)
@click.pass_obj
def update_component(cm, components, only_check, json_output):
    if only_check:
        output, err = cm.update(components, True, json_output)
        if output.strip():
            click.echo(output)
    else:
        cm.update(components)
        os.chdir(os.path.join(cm.project_dir, OS_NAME))
        update_config_in()

# Search command
@cli.command("search", short_help="Search for a component")
@click.argument("keyword", required=True, nargs=-1)
@click.option("--json-output", is_flag=True)
@click.option("-n", "--name", multiple=True)
@click.option("-a", "--author", multiple=True)
@click.pass_obj
def search_component(cm, keyword, json_output, **filters):
    cm.search(keyword)

# Show command
@cli.command("show", short_help="Show detailed info about a component")
@click.argument("component", required=False, nargs=-1)
@click.option("--json-output", is_flag=True)
@click.option("-r", "--remote", is_flag=True, help="List remote components")
@click.pass_obj
def show_component(cm, json_output, remote, component):
    cm.show(json_output, remote, component)

# Clean command
@cli.command("clean", short_help="Clean cached component metadata")
@click.pass_obj
def clean_metadata(cm):
    cm.clean()
