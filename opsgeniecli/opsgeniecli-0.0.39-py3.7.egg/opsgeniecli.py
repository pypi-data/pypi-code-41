#!/usr/bin/env python
# pylint: disable=too-many-lines
# -*- coding: utf-8 -*-
# File: opsgeniecli.py
#
# Copyright 2019 Yorick Hoorneman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for opsgeniecli

.. _Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

"""
from datetime import timedelta
from datetime import datetime
from operator import itemgetter
import urllib.parse
import urllib.request
import os
import collections
import pathlib
import sys
import re
import json
import requests
from prettytable import PrettyTable
import click
import pytz
from opsgenielib import OpsGenie, InvalidApiKey

__author__ = '''Yorick Hoorneman <yhoorneman@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''26-02-2019'''
__copyright__ = '''Copyright 2019, Yorick Hoorneman'''
__credits__ = ["Yorick Hoorneman"]
__license__ = '''MIT'''
__maintainer__ = '''Yorick Hoorneman'''
__email__ = '''<yhoorneman@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


class DefaultHelp(click.Command):
    """Responding with help docs when no arguments are given"""

    def __init__(self, *args, **kwargs):
        context_settings = kwargs.setdefault('context_settings', {})
        if 'help_option_names' not in context_settings:
            context_settings['help_option_names'] = ['-h', '--help']
        self.help_flag = context_settings['help_option_names'][0]
        super(DefaultHelp, self).__init__(*args, **kwargs)

    def parse_args(self, ctx, args):
        if not args:
            args = [self.help_flag]
        return super(DefaultHelp, self).parse_args(ctx, args)


class MutuallyExclusiveOption(click.Option):
    """Restricting parameters to only be usable when a defined other parameter is not used"""

    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = (
                ' NOTE: This argument is mutually exclusive with '
                ' arguments: [' + ex_str + '].'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )


@click.group()
@click.pass_context
@click.option('--config_file', cls=MutuallyExclusiveOption,
              envvar='OPSGENIE_CONFIG',
              mutually_exclusive=["team", "apikey"])
@click.option('--team_name', cls=MutuallyExclusiveOption,
              envvar='OPSGENIE_TEAMNAME',
              mutually_exclusive=["config_file"])
@click.option('--team_id', cls=MutuallyExclusiveOption,
              envvar='OPSGENIE_TEAMID',
              mutually_exclusive=["config_file"])
@click.option('--api_key', cls=MutuallyExclusiveOption,
              envvar='OPSGENIE_APIKEY',
              mutually_exclusive=["config_file"])
@click.option('--profile')
def bootstrapper(context, config_file, team_name, team_id, api_key, profile):  # pylint: disable=too-many-arguments
    """
    Function to sort the authentication used in further calls

    \b
    Args:
        \b
        config_file: option to deviate from the default config location at ~/.opsgenie-cli/config.json
        team_name: teamname in OpsGenie
        team_id: teamid in OpsGenie
        api_key: API key used to authenticate. Note: some calls require an API restricted to a team, most DO NOT
        profile: option to switch between config entries in the config file

    \b
    Returns:
        This function None on success, output shows for incorrect API and misuse of parameters

    """
    if not config_file and not team_name and not api_key and not team_id:
        config_file = pathlib.PurePath(pathlib.Path.home(), ".opsgenie-cli", "config.json")
        if os.path.isfile(config_file):
            with open(config_file) as config_file_path:
                try:
                    data = json.load(config_file_path)
                except ValueError as error:
                    print("invalid json: %s" % error)
                if not profile:
                    profile = 'default'
                context.obj['teamname'] = data[0][profile]['teamname']
                context.obj['apikey'] = data[0][profile]['apikey']
                context.obj['teamid'] = data[0][profile]['teamid']
        else:
            raise click.UsageError(
                "No config was given. Do one of the following:\n"
                "\t-Create a config file at: ~/.opsgenie-cli/config.json\n"
                "\t-Specify a config file. Use --config or set the environment variable OPSGENIE_CONFIG\n"
                "\t-Specify the team & apikey. Use --team & --apikey or set the env vars OPSGENIE_TEAM & OPSGENIE_APIKEY"
            )
    elif config_file:
        with open(config_file) as config_file_path:
            data = json.load(config_file_path)
            if profile:
                context.obj['teamname'] = data[0][profile]['teamname']
                context.obj['apikey'] = data[0][profile]['apikey']
                context.obj['teamid'] = data[0][profile]['teamid']
            else:
                context.obj['teamname'] = data[0]['default']['teamname']
                context.obj['apikey'] = data[0]['default']['apikey']
                context.obj['teamid'] = data[0]['default']['teamid']
    elif team_name and api_key and team_id:
        context.obj['teamname'] = team_name
        context.obj['apikey'] = api_key
        context.obj['teamid'] = team_id
    try:
        context.obj['opsgenie'] = OpsGenie(f"{context.obj['apikey']}")
    except InvalidApiKey:
        raise SystemExit('I am sorry to say that the provided api key is invalid.')


@bootstrapper.group()
@click.pass_context
def alerts(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@alerts.command(name='query',
                help='Example: "status: closed AND teams: <opsgenie-team> AND description: *<some-hostname>*"')
@click.option('--query', required=True)
@click.pass_context
def alerts_query(context, query):
    """
    Function to query alerts

    Args:
        query: a query to filter the alerts

    Returns:
        The json output of the alerts on success, None otherwise

    """
    result = context.obj['opsgenie'].query_alerts(query)
    format_table = PrettyTable(['message', 'tags', 'integration', 'createdAt'])
    for alert in result['data']:
        format_table.add_row([alert['message'], alert['tags'], alert['integration']['type'], alert['createdAt']])
    print(format_table)


@alerts.command(cls=DefaultHelp, name='list')
@click.option('--active', default=False, is_flag=True)
@click.option('--more_info', default=False, is_flag=True)
@click.option('--team_name', default=False)
@click.option('--limit', default=50)
@click.pass_context
def alerts_list(context, active, limit, more_info, team_name):
    """
    Function to list alerts

    Args:
        active: filters down to alerts that are not closed and not acknowledged
        limit: amount of alerts shown in output, default is 100
        more_info: adds the column tags, source, and integration to the output
        team_name: shows the alerts for the team specified

    Returns:
        Table output of the list of alerts on success

    """
    if {context.obj.get('teamname')} and not team_name:
        team_name = f"{context.obj.get('teamname')}"
    if not {context.obj.get('teamname')} and not team_name:
        raise click.UsageError(
            "Specify the teamname using --teamname."
        )
    result = context.obj['opsgenie'].list_alerts_by_team(team_name, limit)
    sortedlist = sorted(result['data'], key=itemgetter('status'))
    if more_info:
        format_table = PrettyTable(['id', 'name', 'status', 'acknowledged',
                                    'createdAt', 'tags', 'source', 'integration'])
    else:
        format_table = PrettyTable(['id', 'name', 'status', 'acknowledged', 'createdAt'])
    for item in sortedlist:
        if active:
            if item['status'] == 'open' and not item['acknowledged']:
                created_at = datetime.strptime(item['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
                if more_info:
                    format_table.add_row([item['id'], item['message'], item['status'], item['acknowledged'],
                                          created_at, item['tags'], item['source'], item['integration']['name']])
                else:
                    format_table.add_row([item['id'], item['message'], item['status'], item['acknowledged'], created_at])
        else:
            created_at = datetime.strptime(item['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            if more_info:
                format_table.add_row([item['id'], item['message'], item['status'], item['acknowledged'],
                                      created_at, item['tags'], item['source'], item['integration']['name']])
            else:
                format_table.add_row([item['id'], item['message'], item['status'], item['acknowledged'], created_at])
    print(format_table)


@alerts.command(cls=DefaultHelp, name='get')
@click.option('--id')
@click.pass_context
def alerts_get(context, id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get more information about a single alert

    Args:
        id: the id of the alert

    Returns:
        The json output of the alert on success, None otherwise

    """
    result = context.obj['opsgenie'].get_alerts(id)
    print(json.dumps(result, indent=4, sort_keys=True))


@alerts.command(name='count')
@click.pass_context
def alerts_count(context):
    """
    Function to show which alerts were noisy

    Returns:
        Table output with alerts for an Opsgenie team and the occurrence of the alerts

    """
    url = f"https://api.opsgenie.com/v2/alerts?limit=100&query=teams:{context.obj.get('teamname')}"
    headers = {
        'Authorization': f"GenieKey {context.obj.get('apikey')}",
        'Content-Type': "application/json"
    }
    response = requests.get(url, headers=headers)
    parsed = json.loads(response.text)
    dictionary = collections.Counter(item['message'] for item in parsed['data'])
    sorted_by_count = sorted(dictionary.items(), reverse=True, key=itemgetter(1))
    for alert in sorted_by_count:
        print(f"{alert[1]} - {alert[0]}")


@alerts.command(cls=DefaultHelp, name='acknowledge')
@click.option('--id', prompt=False, cls=MutuallyExclusiveOption, mutually_exclusive=["all"])
@click.option('--all', default=False, is_flag=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.pass_context
def alerts_acknowledge(context, id, all):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to acknowledge a single or all open alerts

    Args:
        id: the id of the alert
        all: acknowledges all open (not closed nor acknowledged) alerts

    Returns:
        The json output from the API on success, None otherwise

    """
    if id:
        result = context.obj['opsgenie'].acknowledge_alerts(id)
        print(json.dumps(result, indent=4, sort_keys=True))
    elif all:
        result = context.obj['opsgenie'].query_alerts(f"teams:{context.obj.get('teamname')}")
        for item in result['data']:
            if item['status'] == 'open' and not item['acknowledged']:
                response = context.obj['opsgenie'].acknowledge_alerts(item['id'])
                if response['result'] == 'Request will be processed':
                    print(f"✓ - alert acknowledged: {item['id']} - {item['message']}")
                else:
                    print(f"x - alert Not acknowledged: {item['id']} - {item['message']}")


@bootstrapper.group()
@click.pass_context
def policy_alerts(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@policy_alerts.command(cls=DefaultHelp, name='get')
@click.option('--id', prompt=True)
@click.option('--team_id')
@click.pass_context
def policy_alerts_get(context, id, team_id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get more information about a single alert policy

    Args:
        id: the id of the alert policy
        team_id: the id of the team

    Returns:
        The json output from the API on success, None otherwise

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "No team id was found. Use --team_id or specify the team id in the config file.\n"
        )
    result = context.obj['opsgenie'].get_notification_policy(id, team_id)
    print(json.dumps(result, indent=4, sort_keys=True))


@policy_alerts.command(cls=DefaultHelp, name='enable')
@click.option('--team_id',
              help='Specify the team id for team-based alert policies instead of global policies.')
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Specify the name of the alert policy you want to enable.')
@click.option('--id', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["filter"],
              help='The id of the alert policy you want to enable.')
@click.pass_context
def policy_alerts_enable(context, team_id, filter, id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to enable alert policies

    Args:
        team_id: the id of the team, to enable an alert policy connected to that team
        filter: a string to search on through existing alert policies. Can't be used together with --id.
        id: the id of the alert policy. Can't be used together with --filter.

    Returns:
        String output specifying which alert policy was enabled on success, None otherwise

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "Specify the team id using --team_id."
        )
    if not any([filter, id]):
        raise click.UsageError("--id or --filter is required")
    if id:
        result = context.obj['opsgenie'].enable_policy(id, team_id)
        if result['result'] == 'Enabled':
            print(f"✓ - alert policy {id} enabled for team: {context.obj.get('teamname')}")
    if filter:
        id = []
        filters_enabled = []
        alert_policies = context.invoke(policy_alerts_list, team_id=team_id, print_output=False)
        for _filt in filter:
            filtered_results = [x for x in alert_policies['data'] if (_filt).lower() in (x['name']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_enabled.append(filtered_results[0]['name'])
            else:
                print(f"\nMultiple alert policies found for: '{_filt}'")
                filtered_format_table = PrettyTable(['id', 'name', 'type', 'enabled'])
                for result in filtered_results:
                    filtered_format_table.add_row([result['id'], result['name'], result['type'], result['enabled']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the alert policy you want to enable', type=str)
                id.append(temp_id)
                filters_enabled.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        result = context.obj['opsgenie'].enable_policy(id, team_id)
        if result['result'] == 'Enabled':
            print(f"✓ - Alert policies enabled: {filters_enabled} for team: '{context.obj.get('teamname')}'")


@policy_alerts.command(cls=DefaultHelp, name='disable')
@click.option('--team_id',
              help='Specify the team id for team-based alert policies instead of global policies.')
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Specify the name of the alert policy you want to disable.')
@click.option('--id', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["filter"],
              help='The id of the alert policy you want to disable.')
@click.pass_context
def policy_alerts_disable(context, team_id, filter, id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to disable alert policies

    Args:
        team_id: the id of the team, to disable an alert policy connected to that team
        filter: a string to search on through existing alert policies. Can't be used together with --id.
        id: the id of the alert policy. Can't be used together with --filter.

    Returns:
        String output specifying which alert policy was disabled on success, None otherwise

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "Specify the team id using --team_id."
        )
    if not any([filter, id]):
        raise click.UsageError("--id or --filter is required")
    if id:
        result = context.obj['opsgenie'].disable_policy(id, team_id)
        if result['result'] == 'Disabled':
            print(f"✓ - alert policy {id} disabled for team: '{context.obj.get('teamname')}'")
    if filter:
        id = []
        filters_disabled = []
        alert_policies = context.invoke(policy_alerts_list, team_id=team_id, print_output=False)
        for _filt in filter:
            filtered_results = [x for x in alert_policies['data'] if (_filt).lower() in (x['name']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_disabled.append(filtered_results[0]['name'])
            else:
                print(f"\nMultiple alert policies found for: '{_filt}'")
                filtered_format_table = PrettyTable(['id', 'name', 'type', 'disabled'])
                for result in filtered_results:
                    filtered_format_table.add_row([result['id'], result['name'], result['type'], result['enabled']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the alert policy you want to disable', type=str)
                id.append(temp_id)
                filters_disabled.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        result = context.obj['opsgenie'].disable_policy(id, team_id)
        if result['result'] == 'Disabled':
            print(f"✓ - Alert policies disabled: {filters_disabled} for team: '{context.obj.get('teamname')}'")


@policy_alerts.command(name='list')
@click.option('--team_id', help='Specify the team id for team-based alert policies instead of global policies.')
@click.pass_context
def policy_alerts_list(context, team_id, print_output=True):  # pylint: disable=inconsistent-return-statements
    """
    Function to list alert policies

    Args:
        team_id: the id of the team to list alert policies for

    Returns:
        Table output listing alert policies in the format of three columns: ID, Name, and Enabled (boolean)

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "Specify the team id using --team_id."
        )
    result = context.obj['opsgenie'].list_alert_policy(team_id)
    format_table = PrettyTable(['teamid', 'name', 'enabled'])
    for item in result['data']:
        format_table.add_row([item['id'], item['name'], item['enabled']])
    if print_output:
        print(format_table)
    else:
        return result


@policy_alerts.command(cls=DefaultHelp, name='delete')
@click.option('--id', help='The id of the alerts policy that will be deleted.',
              cls=MutuallyExclusiveOption, mutually_exclusive=["filter"])
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Filter based on the name of the maintenance policy.')
@click.option('--all', default=False, is_flag=True, help='Will remove all alerts policies for the team.',
              cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.option('--team_id', help='Specify the team id.')
@click.pass_context
def policy_alerts_delete(context, id, all, team_id, filter):  # pylint: disable=redefined-builtin, invalid-name, too-many-locals, too-many-branches
    """
    Function to delete a single or multiple alerts

    Args:
        id: the id of the alert policy
        all: shows all alert policies that will be deleted, deletion follows after a prompts
        team_id: the id of the team to remove alert policies for

    Returns:
        String output specifying which alert policy id was removed and for which team on success, None otherwise

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "Specify the team id using --team_id."
        )
    if id:
        response = context.obj['opsgenie'].delete_alert_policy(id, team_id)
        if response['result'] == 'Deleted':
            print(f"✓ - alert policy {id} deleted for team: {context.obj.get('teamname')}")
    elif all:
        reponse = context.obj['opsgenie'].list_alert_policy(team_id)
        print("The following alerts policies will be deleted:")
        for item in reponse['data']:
            print(f"{item['id']} - {item['name']}")
        value = click.confirm('\nDo you want to continue?', abort=True)
        if value:
            for item in reponse['data']:
                response = context.obj['opsgenie'].delete_alert_policy(f"{item['id']}", team_id)
                if response['result'] == 'Deleted':
                    print(f"✓ - alert policy {item['id']} deleted for team: {context.obj.get('teamname')}")
    elif filter:
        id = []
        filters_deleted = []
        alert_policies = context.obj['opsgenie'].list_alert_policy(team_id)
        for _filt in filter:
            filtered_results = [x for x in alert_policies['data'] if (_filt).lower() in (x['name']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_deleted.append(filtered_results[0]['name'])
            else:
                print(f"\nMultiple alert filters found for: '{_filt}'.")
                filtered_format_table = PrettyTable(['teamid', 'name', 'enabled'])
                for f_result in filtered_results:
                    filtered_format_table.add_row([f_result['id'],
                                                   f_result['name'],
                                                   f_result['enabled']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the policy you want to delete', type=str)
                id.append(temp_id)
                filters_deleted.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        del_result = context.obj['opsgenie'].delete_alert_policy(id, team_id)
        if del_result['result'] == 'Deleted':
            print(f"✓ - Alert policies deleted: {filters_deleted}")
    else:
        raise click.UsageError(
            "Use --id, --all or --filter to delete one or multiple alert policies"
        )

# @policy_alerts.command(cls=DefaultHelp, name='set')
# @click.option('--name', help='Name of the policy.')
# @click.option('--enabled', default=True, is_flag=True, help='Initial status of the integration.')
# @click.option('--team_id', help='Specify the team id.')
#               # Later? functionality that by default grabs the teamid from the config.
# @click.option('--message', default='{{message}}', help='Message of the alert.')
# @click.option('--filter_type', type=click.Choice(['match-all', 'match-any-condition', 'match-all-conditions']),
#               help='The type of filtering the policy applies for the alerts.')
# @click.option('--filter_type', type=click.Choice(['match-all', 'match-any-condition', 'match-all-conditions']),
#               help='The type of filtering the policy applies for the alerts.')
# @click.pass_context
# def policy_alerts_set(context, id, all, team_id):  # pylint: disable=redefined-builtin, invalid-name
#     """
#     Function to delete a single or multiple alerts

#     Args:
#         id: the id of the alert policy
#         all: shows all alert policies that will be deleted, deletion follows after a prompts
#         team_id: the id of the team to remove alert policies for

#     Returns:
#         String output specifying which alert policy id was removed and for which team on success, None otherwise

#     """
#     if {context.obj.get('teamid')} and not team_id:
#         team_id = f"{context.obj.get('teamid')}"
#     if not {context.obj.get('teamid')} and not team_id:
#         raise click.UsageError(
#             "Specify the team id using --team_id."
#         )
#     if id:
#         response = context.obj['opsgenie'].delete_alert_policy(id, team_id)
#         if response['result'] == 'Deleted':
#             print(f"✓ - alert policy {id} deleted for team: {context.obj.get('teamname')}")
#         else:
#             print(response.text)
#             sys.exit(1)
#     if all:
#         reponse = context.obj['opsgenie'].list_alert_policy(team_id)
#         print("The following alerts policies will be deleted:")
#         for item in reponse['data']:
#             print(f"{item['id']} - {item['name']}")
#         value = click.confirm('\nDo you want to continue?', abort=True)
#         if value:
#             for item in reponse['data']:
#                 response = context.obj['opsgenie'].delete_alert_policy(f"{item['id']}", team_id)
#                 if response['result'] == 'Deleted':
#                     print(f"✓ - alert policy {item['id']} deleted for team: {context.obj.get('teamname')}")
#                 else:
#                     print(response.text)
#                     sys.exit(1)


@bootstrapper.group()
@click.pass_context
def integrations(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@integrations.command(cls=DefaultHelp, name='list')
@click.option('--id', cls=MutuallyExclusiveOption, mutually_exclusive=["team_name"])
@click.option('--team_name', cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.pass_context
def integrations_list(context, id, team_name):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to list integrations

    Args:
        id: the id of the team to list integrations for
        team_name: the teamname of the team to list integrations for

    Returns:
        Table output listing integrations in the format of five columns: type, id, name, teamId, enabled (boolean)

    """
    if id:
        result = context.obj['opsgenie'].list_integrations_by_team_id(id)
    elif team_name:
        result = context.obj['opsgenie'].list_integrations_by_team_name(team_name)
    else:
        raise click.UsageError(
            "Specify the team name or team id using --team_name or --id."
        )
    format_table = PrettyTable(['type', 'id', 'name', 'teamId', 'enabled'])
    for item in result['data']:
        format_table.add_row([item['type'], item['id'], item['name'], item['teamId'], item['enabled']])
    print(format_table)


@integrations.command(cls=DefaultHelp, name='get')
@click.option('--id', required=True)
@click.pass_context
def integrations_get(context, id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get more information about a single integrations

    Args:
        id: the id of the integration

    Returns:
        The json output from the API on success, None otherwise

    """
    result = context.obj['opsgenie'].get_integrations(id)
    print(json.dumps(result, indent=4, sort_keys=True))


@bootstrapper.group()
@click.pass_context
def config(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@config.command(cls=DefaultHelp, name='list')
@click.option('--config', default="~/.opsgenie-cli/config.json", envvar='OPSGENIE_CONFIG')
def config_list(config):  # pylint: disable=redefined-outer-name
    """Function that shows the entries in the config file"""
    if "~" in config:
        config = os.path.expanduser(config)
    with open(config) as config_file:
        data = json.load(config_file)
        for i in data[0]:
            print(json.dumps(i, indent=4, sort_keys=True))


@bootstrapper.group()
@click.pass_context
def policy_maintenance(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@policy_maintenance.command(cls=DefaultHelp, name='get')
@click.option('--id', prompt=True)
@click.pass_context
def policy_maintenance_get(context, id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get more information about a single maintenance policy

    Args:
        id: the id of the maintenance policy

    Returns:
        The json output from the API on success, None otherwise

    """
    result = context.obj['opsgenie'].get_maintenance_policy(id)
    print(json.dumps(result, indent=4, sort_keys=True))


@policy_maintenance.command(cls=DefaultHelp, name='set')
@click.option('--description', prompt=True)
@click.option('--start_date', help='Example: 2019-03-15T14:34:09Z')
@click.option('--end_date', help='Example: 2019-03-15T15:34:09Z')
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Filter down based on the name of the alert policy.')
@click.option('--state', type=click.Choice(['enabled', 'disabled']), default='enabled', help='State of rule that \
    will be defined in maintenance and can take \
    either enabled or disabled for policy type rules. This field has to be disabled for integration type entity rules')
@click.option('--entity', type=click.Choice(['integration', 'policy']), default='policy', help='The type of the entity \
    that maintenance will be applied. It can be either integration or policy')
@click.option('--hours', type=int, help='Filter duration is hours.')
@click.option('--id', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["filter"],
              help='The id of the entity that maintenance will be applied.')
@click.pass_context
def policy_maintenance_set(context,  # pylint: disable=too-many-branches, too-many-arguments, too-many-locals, invalid-name
                           description,
                           id,  # pylint: disable=redefined-builtin
                           state,
                           entity,
                           hours,
                           filter,  # pylint: disable=redefined-builtin
                           start_date,
                           end_date):
    """
    Function to create a maintenance policy

    Args:
        description: the name of the maintenance policy
        id: the id of the entity (integration or alert- or notification policies) used in the maintenance policy
        state: the state of the maintenance rule, enabled or disabled
        entity: the entity allows filtering using policies or a whole integrations
        hours: setting a maintenance policy from now plus the specified amount of hours
        filter: instead of specifying the id, using the name of the policy. Returns list that matches the filter
        start_date: a date and time on which the maintenance policy should start
        end_date: a date and time on which the maintenance policy should end

    Returns:
        String output names the title and the start- and end date of the maintenance policy on success, None otherwise

    """
    if not any([filter, id]):
        raise click.UsageError("--id or --filter is required")
    if filter:
        id = []
        filters_enabled = []
        result = context.obj['opsgenie'].list_alert_policy(context.obj.get('teamid'))
        for _filt in filter:
            filtered_results = [x for x in result['data'] if (_filt).lower() in (x['name']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_enabled.append(filtered_results[0]['name'])
            else:
                print(f"\nMultiple maintenance filters found for {_filt}.")
                filtered_format_table = PrettyTable(['id', 'name', 'type', 'enabled'])
                for result in filtered_results:
                    filtered_format_table.add_row([result['id'], result['name'], result['type'], result['enabled']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the filter you want to use', type=str)
                id.append(temp_id)
                filters_enabled.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
    if all([start_date, end_date]):
        start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")
        startdatetime = start.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        enddatetime = end.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        start = datetime.now().astimezone(pytz.utc)
        end = start + timedelta(hours=hours)
    if hours:
        result = context.obj['opsgenie'].set_maintenance_policy_hours(context.obj.get('teamid'),
                                                                      hours,
                                                                      entity,
                                                                      description,
                                                                      state,
                                                                      id)
    if all([start_date, end_date]):
        result = context.obj['opsgenie'].set_maintenance_policy_schedule(context.obj.get('teamid'),
                                                                         startdatetime,
                                                                         enddatetime,
                                                                         entity,
                                                                         description,
                                                                         state,
                                                                         id)
    if result.status_code == 201:
        if hours:
            print(f"✓ - Maintenance policy created.\n\t"
                  f"Description: {description}\n\t"
                  f"Time: {hours}hours\n\t"
                  f"Policies enabled: {filters_enabled}")
        if start_date and end_date:
            startdatetime = start.strftime('%Y-%m-%d %H:%M:%S')
            enddatetime = end.strftime('%Y-%m-%d %H:%M:%S')
            print(f"✓ - Maintenance policy created.\n\t"
                  f"Description: {description}\n\t"
                  f"Time: from {startdatetime} - {enddatetime}\n\t"
                  f"Policies enabled: {filters_enabled}")


@policy_maintenance.command(cls=DefaultHelp, name='cancel')
@click.option('--id', multiple=True, cls=MutuallyExclusiveOption,
              mutually_exclusive=["filter"])
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Filter based on the name of the maintenance policy.')
@click.pass_context
def policy_maintenance_cancel(context, id, filter):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to cancel a single maintenance policy

    Args:
        id: the id of the maintenance policy
        filter: the name or a part of a maintenance policy. In the case of multiple results,
        the results are displayed with a choice to select one.

    Returns:
        String output specifying which maintenance policy id was canceled and for which team on success, None otherwise

    """
    if id:
        result = context.obj['opsgenie'].cancel_maintenance_policy(id)
        if result['result'] == 'Cancelled':
            print(f"✓ - Maintenance policies canceled: {id}")
    if filter:
        id = []
        filters_canceled = []
        maintenance_policies = context.obj['opsgenie'].list_maintenance_policy_by_team_id(
            context.obj.get('teamid'),
            non_expired=True)
        for _filt in filter:
            filtered_results = [x for x in maintenance_policies['data'] if (_filt).lower() in (x['description']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_canceled.append(filtered_results[0]['description'])
            else:
                print(f"\nMultiple maintenance filters found for: '{_filt}'.")
                filtered_format_table = PrettyTable(['id', 'description', 'status', 'type'])
                for f_result in filtered_results:
                    filtered_format_table.add_row([f_result['id'],
                                                   f_result['description'],
                                                   f_result['status'],
                                                   f_result['time']['type']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the policy you want to cancel', type=str)
                id.append(temp_id)
                filters_canceled.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        result = context.obj['opsgenie'].cancel_maintenance_policy(id)
        if result['result'] == 'Cancelled':
            print(f"✓ - Maintenance policies canceled: {filters_canceled}")
    else:
        raise click.UsageError(
            "Use --id or --filter to cancel one or multiple maintenance policies"
        )


@policy_maintenance.command(cls=DefaultHelp, name='delete')
@click.option('--id', multiple=True, cls=MutuallyExclusiveOption,
              mutually_exclusive=["filter"])
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Filter based on the name of the maintenance policy.')
@click.option('--all', default=False, is_flag=True, help='Will remove all maintenance policies for the team.',
              cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.option('--team_id', help='Option to specify the id of the team.\
              the team id of the config file is used when no --team_id is given.')
@click.pass_context
def policy_maintenance_delete(context, id, all, team_id, filter):  # pylint: disable=redefined-builtin, invalid-name, too-many-locals, too-many-branches
    """
    Function to delete a single or all maintenance policies

    Args:
        id: the id of the maintenance policy
        filter: the name or a part of a maintenance policy. In the case of multiple results,
        the results are displayed with a choice to select one.
        all: shows all maintenance policies that will be deleted, deletion follows after a prompts
        team_id: the id of the team

    Returns:
        String output specifying which maintenance policy id was removed and for which team on success, None otherwise

    """
    if context.obj.get('teamid') and not team_id:
        team_id = context.obj.get('teamid')
    if id:
        result = result = context.obj['opsgenie'].delete_maintenance_policy(id)
        if result.status_code == 200:
            print(f"✓ - Maintenance policies deleted: {id}")
    elif all:
        result = context.obj['opsgenie'].list_maintenance_policy(team_id)
        print("The following maintenance policies will be deleted:")
        for item in result['data']:
            print(f"{item['id']} - {item['description']}")
        value = click.confirm('\nDo you want to continue?', abort=True)
        if value:
            for item in result['data']:
                result = context.obj['opsgenie'].delete_maintenance_policy(item['id'])
                if result.status_code == 200:
                    print(f"✓ - maintenance policy {item['id']} deleted for team: {context.obj.get('teamname')}")
    elif filter:
        id = []
        filters_deleted = []
        maintenance_policies = context.obj['opsgenie'].list_maintenance_policy_by_team_id(
            context.obj.get('teamid'),
            non_expired=True)
        for _filt in filter:
            filtered_results = [x for x in maintenance_policies['data'] if (_filt).lower() in (x['description']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_deleted.append(filtered_results[0]['description'])
            else:
                print(f"\nMultiple maintenance filters found for: '{_filt}'.")
                filtered_format_table = PrettyTable(['id', 'description', 'status', 'type'])
                for f_result in filtered_results:
                    filtered_format_table.add_row([f_result['id'],
                                                   f_result['description'],
                                                   f_result['status'],
                                                   f_result['time']['type']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the policy you want to delete', type=str)
                id.append(temp_id)
                filters_deleted.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        del_result = context.obj['opsgenie'].delete_maintenance_policy(id)
        if del_result.status_code == 200:
            print(f"✓ - Maintenance policies deleted: {filters_deleted}")
    else:
        raise click.UsageError(
            "Use --id, --all or --filter to delete one or multiple maintenance policies"
        )


@policy_maintenance.command(name='list')
@click.option('--nonexpired', '--active', default=False,
              is_flag=True, cls=MutuallyExclusiveOption, mutually_exclusive=["past"])
@click.option('--past', default=False, is_flag=True,
              cls=MutuallyExclusiveOption, mutually_exclusive=["non-expired"])
@click.option('--team_id', help='Option to specify the id of the team.\
              the team id of the config file is used when no --team_id is given.')
@click.pass_context
def policy_maintenance_list(context, nonexpired, past, team_id):
    """
    Function to list a maintenance policies

    Args:
        nonexpired: lists only maintenance policies that are active or scheduled
        past: lists expired maintenance policies
        team_id: the id of the team

    Returns:
        Table output listing maintenance policies in the format of five columns:
        id, status, description, type and startdate

    """
    if context.obj.get('teamid') and not team_id:
        team_id = context.obj.get('teamid')
    if nonexpired:
        result = context.obj['opsgenie'].list_maintenance_policy_by_team_id(team_id, non_expired=True)
    elif past:
        result = context.obj['opsgenie'].list_maintenance_policy_by_team_id(team_id, past=True)
    else:
        result = context.obj['opsgenie'].list_maintenance_policy_by_team_id(team_id)
    format_table = PrettyTable(['id', 'status', 'description', 'type', 'startdate'])
    for item in result['data']:
        truncated_start_date = (item['time']['startDate'].replace('Z', '')).split(".")[0]
        modified_format = datetime.fromisoformat(truncated_start_date).strftime('%Y-%m-%d %H:%M:%S')
        format_table.add_row([item['id'], item['status'], item['description'],
                              item['time']['type'], modified_format])
    print(format_table)


@bootstrapper.group()
@click.pass_context
def heartbeat(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@heartbeat.command(cls=DefaultHelp, name='ping')
@click.option('--heartbeat_name', help='The name of the heartbeat.')
@click.pass_context
def heartbeat_ping(context, heartbeat_name):
    """
    Function to ping a heartbeat

    Args:
        heartbeat_name: the name of the heartbeat

    Returns:
        The json output from the API on success, None otherwise

    """
    result = context.obj['opsgenie'].ping_heartbeat(heartbeat_name)
    print(json.dumps(result, indent=4, sort_keys=True))


@heartbeat.command(cls=DefaultHelp, name='get')
@click.option('--heartbeat_name', help='The name of the heartbeat.')
@click.pass_context
def heartbeat_get(context, heartbeat_name):
    """
    Function to get more information about a single heartbeat

    Args:
        heartbeat_name: the name of the heartbeat

    Returns:
        The json output from the API on success, None otherwise

    """
    result = context.obj['opsgenie'].get_heartbeat(heartbeat_name)
    print(json.dumps(result, indent=4, sort_keys=True))


@heartbeat.command(name='list')
@click.pass_context
def heartbeat_list(context):
    """
    Function to get more information about a single heartbeat

    Returns:
        The json output from the API on success, None otherwise

    """
    result = context.obj['opsgenie'].list_heartbeats()
    print(json.dumps(result, indent=4, sort_keys=True))


@heartbeat.command(cls=DefaultHelp, name='enable')
@click.option('--heartbeat_name', help='The name of the heartbeat.')
@click.pass_context
def heartbeat_enable(context, heartbeat_name):
    """
    Function to enable a single heartbeat

    Args:
        heartbeat_name: the name of the heartbeat

    Returns:
        The json output from the API on success, None otherwise

    """
    result = context.obj['opsgenie'].enable_heartbeat(heartbeat_name)
    print(json.dumps(result, indent=4, sort_keys=True))


@heartbeat.command(cls=DefaultHelp, name='disable')
@click.option('--heartbeat_name', help='The name of the heartbeat.')
@click.pass_context
def heartbeat_disable(context, heartbeat_name):
    """
    Function to enable a disable heartbeat

    Args:
        heartbeat_name: the name of the heartbeat

    Returns:
        The json output from the API on success, None otherwise

    """
    result = context.obj['opsgenie'].disable_heartbeat(heartbeat_name)
    print(json.dumps(result, indent=4, sort_keys=True))


@bootstrapper.group()
def teams():
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@teams.command(cls=DefaultHelp, name='get')
@click.option('--id', cls=MutuallyExclusiveOption, mutually_exclusive=["team_name"])
@click.option('--team_name', cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.pass_context
def teams_get(context, id, team_name):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get more information about a team

    Args:
        id: the id of the team
        team_name: the name of the team

    Returns:
        Table output listing the team members of a team in the format of two columns: id's and usernames

    """
    if id:
        result = context.obj['opsgenie'].get_team_by_id(id)
    elif team_name:
        result = context.obj['opsgenie'].get_team_by_name(team_name)
    format_table = PrettyTable([result['data']['name'] + ' ids', result['data']['name'] + ' usernames'])
    for item in result['data']['members']:
        format_table.add_row([item['user']['id'], item['user']['username']])
    print(format_table)


@teams.command(cls=DefaultHelp, name='logs')
@click.option('--id', cls=MutuallyExclusiveOption, mutually_exclusive=["team_name"])
@click.option('--team_name', cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.pass_context
def teams_logs(context, id, team_name):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get the team logs

    Args:
        id: the id of the team
        team_name: the name of the team

    Returns:
        The json output from the API on success, None otherwise

    """
    if {context.obj.get('teamname')} and not team_name:
        team_name = f"{context.obj.get('teamname')}"
    if not {context.obj.get('teamname')} and not {context.obj.get('id')} and not team_name and not id:
        raise click.UsageError(
            "Specify the name of the team using --team_name or the id of the team using --id."
        )
    if id:
        result = context.obj['opsgenie'].get_team_logs_by_id(id)
    elif team_name:
        result = context.obj['opsgenie'].get_team_logs_by_name(team_name)
    print(json.dumps(result, indent=4, sort_keys=True))


@teams.command(name='list')
@click.pass_context
def teams_list(context):
    """
    Function to list all the teams

    Returns:
        Table output listing the teams in the format of two columns: team id's and team names

    """
    result = context.obj['opsgenie'].list_teams()
    test = find_team_by_name('team5')
    format_table = PrettyTable(['id', 'name'])
    for item in result['data']:
        format_table.add_row([item['id'], item['name']])
    print(format_table)

@click.pass_context
def find_team_by_name(context, team_name):
    """ Function to find a team_id, based on a team_name.  """
    teams_found = context.obj['opsgenie'].list_teams()
    filtered_teams = [x for x in teams_found['data'] if re.findall(rf"\b{team_name}\b", x['name'])]
    if len(filtered_teams) == 1:
        print(filtered_teams[0]['name'])
        return filtered_teams[0]['id']
    elif len(filtered_teams) > 1:
        format_table = PrettyTable(['id', 'name'])
        for item in filtered_teams:
            format_table.add_row([item['id'], item['name']])
        print(f'Multiple teams found for {team_name}: \n{format_table}')
        team_id = ""
        while len(team_id) < 30:
            team_id = click.prompt('Enter the id of the team you want', type=str)
        return team_id
    else:
        print(f'No teams found for {team_name}')


@bootstrapper.group()
def teams_routing_rules():
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@teams_routing_rules.command(cls=DefaultHelp, name='list')
@click.option('--id', cls=MutuallyExclusiveOption, mutually_exclusive=["team_name"])
@click.option('--team_name', cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.pass_context
def teams_routing_list(context, id, team_name):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to list all the information about the routing of alerts for a team

    Args:
        id: the id of the team
        team_name: the name of the team

    Returns:
        The json output from the API on success, None otherwise

    """
    if id:
        result = context.obj['opsgenie'].get_routing_rules_by_id(id)
    elif team_name:
        result = context.obj['opsgenie'].get_routing_rules_by_name(team_name)
    else:
        raise click.UsageError(
            "No team id or team name was specified. Use --id or --team_name.\n"
        )
    print(json.dumps(result, indent=4, sort_keys=True))


@bootstrapper.group()
def escalations():
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@escalations.command(cls=DefaultHelp, name='get')
@click.option('--id', cls=MutuallyExclusiveOption, mutually_exclusive=["escalation_name"])
@click.option('--escalation_name', cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.pass_context
def escalations_get(context, id, escalation_name):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to list to get more information about a single escalation

    Args:
        id: the id of the escalation
        escalation_name: the name of the escalation

    Returns:
        The json output from the API on success, None otherwise

    """
    if id:
        result = context.obj['opsgenie'].get_escalations_by_id(id)
    elif escalation_name:
        result = context.obj['opsgenie'].get_escalations_by_name(escalation_name)
    else:
        raise click.UsageError(
            "No escalation id or escalation name was specified. Use --id or --escalation_name.\n"
        )
    print(json.dumps(result, indent=4, sort_keys=True))


@escalations.command(name='list')
@click.pass_context
def escalations_list(context):
    """
    Function to list the escalation for each team

    Returns:
        Table output listing the teams in the format of three columns: id's, escalation name, and ownerTeam

    """
    result = context.obj['opsgenie'].list_escalations()
    format_table = PrettyTable(['id', 'name', 'ownerTeam'])
    for item in result['data']:
        format_table.add_row([item['id'], item['name'], item['ownerTeam']['name']])
    print(format_table)


@bootstrapper.group()
@click.pass_context
def schedules(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@schedules.command(cls=DefaultHelp, name='get')
@click.option('--id', cls=MutuallyExclusiveOption, mutually_exclusive=["schedule_name"])
@click.option('--schedule_name', cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.pass_context
def schedules_get(context, id, schedule_name):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get more information about a single schedule

    Args:
        id: the id of the escalation
        schedule_name: the name of the escalation

    Returns:
        The json output from the API on success, None otherwise

    """
    if id:
        result = context.obj['opsgenie'].get_schedules_by_id(id)
    elif schedule_name:
        result = context.obj['opsgenie'].get_schedules_by_name(schedule_name)
    else:
        raise click.UsageError(
            "No schedule id or schedule name was specified. Use --id or --schedule_name.\n"
        )
    print(json.dumps(result, indent=4, sort_keys=True))


@schedules.command(name='list')
@click.pass_context
def schedules_list(context):
    """
    Function to list the schedules for all teams

    Returns:
        Table output listing the schedules for all teams in the format of two columns: id and name

    """
    result = context.obj['opsgenie'].list_schedules()
    sortedlist = sorted(result['data'], key=itemgetter('name'))
    format_table = PrettyTable(['id', 'name'])
    for item in sortedlist:
        format_table.add_row([item['id'], item['name']])
    print(format_table)


@bootstrapper.group()
@click.pass_context
def logs(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@logs.command(cls=DefaultHelp, name='download')
@click.option('--marker', required=True)
@click.option('--download_path', required=True)
@click.option('--limit')
@click.pass_context
def logs_download(context, marker, limit, download_path):
    """
    Function to download logs

    Args:
        marker: download logs since a certain date, called the marker
        limit: maximum amount of files that are downloaded
        download_path: local location to store the log files

    Returns:
        String output on the progress and the log files at the specified download location

    """
    if limit and marker:
        result = context.obj['opsgenie'].get_logs_filenames(marker, limit)
    if marker and not limit:
        result = context.obj['opsgenie'].get_logs_filenames(marker)
    result = context.obj['opsgenie'].get_logs_filenames(id)
    total_count = len(result['data'])
    current_count = 1
    for file in result['data']:
        print(f"{current_count} - {total_count} - downloading {file['filename']}")
        download_url = context.obj['opsgenie'].get_logs_download_link(file['filename'])
        urllib.request.urlretrieve(download_url.text, f"{download_path}/{file['filename']}")
        current_count = current_count + 1


@bootstrapper.group()
@click.pass_context
def policy_notifications(context):  # pylint: disable=unused-argument
    """Sub-command for Opsgeniecli. This function is a placeholder to maintain the correct hierarchy for the cli"""
    pass


@policy_notifications.command(cls=DefaultHelp, name='enable')
@click.option('--team_id',
              help='Specify the team id for team-based notification policies instead of global policies.')
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Specify the name of the notification policy you want to enable.')
@click.option('--id', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["filter"],
              help='The id of the notification policy you want to enable.')
@click.pass_context
def policy_notifications_enable(context, team_id, filter, id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to enable notification policies

    Args:
        team_id: the id of the team, to enable a notification policy connected to that team
        filter: a string to search on through existing notification policies. Can't be used together with --id.
        id: the id of the notification policy. Can't be used together with --filter.

    Returns:
        String output specifying which notification policy was enabled on success, None otherwise

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "Specify the team id using --team_id."
        )
    if not any([filter, id]):
        raise click.UsageError("--id or --filter is required")
    if id:
        result = context.obj['opsgenie'].enable_policy(id, team_id)
        if result['result'] == 'Enabled':
            print(f"✓ - Notification policy {id} enabled for team: '{context.obj.get('teamname')}'")
    if filter:
        id = []
        filters_enabled = []
        notifications_policies = context.invoke(policy_notifications_list, team_id=team_id, print_output=False)
        for _filt in filter:
            filtered_results = [x for x in notifications_policies['data'] if (_filt).lower() in (x['name']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_enabled.append(filtered_results[0]['name'])
            else:
                print(f"\nMultiple notifications policies found for: '{_filt}'")
                filtered_format_table = PrettyTable(['id', 'name', 'type', 'enabled'])
                for result in filtered_results:
                    filtered_format_table.add_row([result['id'], result['name'], result['type'], result['enabled']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the notifications policy you want to enable', type=str)
                id.append(temp_id)
                filters_enabled.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        result = context.obj['opsgenie'].enable_policy(id, team_id)
        if result['result'] == 'Enabled':
            print(f"✓ - Notifications policies enabled: {filters_enabled} for team: '{context.obj.get('teamname')}'")


@policy_notifications.command(cls=DefaultHelp, name='disable')
@click.option('--team_id',
              help='Specify the team id for team-based notification policies instead of global policies.')
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Specify the name of the notification policy you want to disable.')
@click.option('--id', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["filter"],
              help='The id of the notification policy you want to disable.')
@click.pass_context
def policy_notifications_disable(context, team_id, filter, id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to disable notification policies

    Args:
        team_id: the id of the team, to disable a notification policy connected to that team
        filter: a string to search on through existing notification policies. Can't be used together with --id.
        id: the id of the notification policy. Can't be used together with --filter.

    Returns:
        String output specifying which notification policy was disabled on success, None otherwise

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "Specify the team id using --team_id."
        )
    if not any([filter, id]):
        raise click.UsageError("--id or --filter is required")
    if id:
        result = context.obj['opsgenie'].disable_policy(id, team_id)
        if result['result'] == 'Disabled':
            print(f"✓ - Notification policy {id} disabled for team: '{context.obj.get('teamname')}'")
    if filter:
        id = []
        filters_disabled = []
        notifications_policies = context.invoke(policy_notifications_list, team_id=team_id, print_output=False)
        for _filt in filter:
            filtered_results = [x for x in notifications_policies['data'] if (_filt).lower() in (x['name']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_disabled.append(filtered_results[0]['name'])
            else:
                print(f"\nMultiple notifications policies found for: '{_filt}'")
                filtered_format_table = PrettyTable(['id', 'name', 'type', 'enabled'])
                for result in filtered_results:
                    filtered_format_table.add_row([result['id'], result['name'], result['type'], result['enabled']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the notifications policy you want to disable', type=str)
                id.append(temp_id)
                filters_disabled.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        result = context.obj['opsgenie'].disable_policy(id, team_id)
        if result['result'] == 'Disabled':
            print(f"✓ - Notifications policies disabled: {filters_disabled} for team: '{context.obj.get('teamname')}'")


@policy_notifications.command(cls=DefaultHelp, name='get')
@click.option('--id', prompt=True)
@click.option('--team_id')
@click.pass_context
def policy_notifications_get(context, id, team_id):  # pylint: disable=redefined-builtin, invalid-name
    """
    Function to get more information about a single notification policy

    Args:
        id: the id of the notification policy
        team_id: the id of the team

    Returns:
        The json output from the API on success, None otherwise

    """
    if team_id:
        result = context.obj['opsgenie'].get_notification_policy(id, team_id)
    elif context.obj.get('teamid') and not team_id:
        result = context.obj['opsgenie'].get_notification_policy(id, context.obj.get('teamid'))
    else:
        raise click.UsageError(
            "No team id was found. Use --team_id or specify the team id in the config file.\n"
        )
    print(json.dumps(result, indent=4, sort_keys=True))


@policy_notifications.command(cls=DefaultHelp, name='delete')
@click.option('--id', multiple=True, help='The id of the notifications policy that will be deleted.',
              cls=MutuallyExclusiveOption, mutually_exclusive=["filter"])
@click.option('--filter', multiple=True, cls=MutuallyExclusiveOption, mutually_exclusive=["id"],
              help='Filter based on the name of the notifications policy.')
@click.option('--all', default=False, is_flag=True, help='Will remove all notifications policies for the team.',
              cls=MutuallyExclusiveOption, mutually_exclusive=["id"])
@click.option('--team_id', help='Specify the team id.')
@click.pass_context
def policy_notifications_delete(context, id, team_id, all, filter):  # pylint: disable=redefined-builtin, invalid-name, too-many-branches, too-many-locals
    """
    Function to delete a single or all notifications policies

    Args:
        id: the id of the notification policies
        all: shows all notification policies that will be deleted, deletion follows after a prompts
        filter: a string to search on through existing notifications policies. Can't be used together with --id
        team_id: the id of the team to remove notifications policies for

    Returns:
        String output specifying which notification policy id was removed and for which team on success, None otherwise

    """
    if {context.obj.get('teamid')} and not team_id:
        team_id = f"{context.obj.get('teamid')}"
    if not {context.obj.get('teamid')} and not team_id:
        raise click.UsageError(
            "Specify the team id using --team_id."
        )
    if id:
        result = context.obj['opsgenie'].get_notification_policy(id, team_id)
        if result.status_code == 200:
            print(f"✓ - notification policy {id} deleted for team: {context.obj.get('teamname')}")
        else:
            print(result.text)
            sys.exit(1)
    elif all:
        result = context.obj['opsgenie'].list_notification_policy(team_id)
        print("The following notifications policies will be deleted:")
        for item in result['data']:
            print(f"{item['id']} - {item['name']}")
        value = click.confirm('\nDo you want to continue?', abort=True)
        if value:
            for item in result['data']:
                result = context.obj['opsgenie'].delete_notification_policy(item['id'], team_id)
                if result.status_code == 200:
                    print(f"notifications policy {item['id']} deleted for team: {context.obj.get('teamname')}")
                else:
                    print(result.text)
                    sys.exit(1)
    elif filter:
        id = []
        filters_deleted = []
        notifications_policies = context.obj['opsgenie'].list_notification_policy(team_id)
        for _filt in filter:
            filtered_results = [x for x in notifications_policies['data'] if (_filt).lower() in (x['name']).lower()]
            if len(filtered_results) == 1:
                id.append(filtered_results[0]['id'])
                filters_deleted.append(filtered_results[0]['name'])
            else:
                print(f"\nMultiple notifications filters found for: '{_filt}'.")
                filtered_format_table = PrettyTable(['teamid', 'name', 'enabled'])
                for f_result in filtered_results:
                    filtered_format_table.add_row([f_result['id'],
                                                   f_result['name'],
                                                   f_result['enabled']])
                print(filtered_format_table)
                temp_id = ""
                while len(temp_id) < 30:
                    temp_id = click.prompt('Enter the id of the policy you want to delete', type=str)
                id.append(temp_id)
                filters_deleted.append([item['name'] for item in filtered_results if item.get('id') == temp_id][0])
        del_result = context.obj['opsgenie'].delete_notification_policy(id, team_id)
        if del_result.status_code == 200:
            print(f"✓ - Notifications policies deleted: {filters_deleted}")
    else:
        raise click.UsageError(
            "Use --id, --all or --filter to delete one or multiple notifications policies"
        )


@policy_notifications.command(cls=DefaultHelp, name='list')
@click.option('--team_id', help='Specify the id of the team. \
              The teamid from the config is used when no --team_id argument is given.')
@click.option('--non_expired', '--active', default=False, is_flag=True)
@click.pass_context
def policy_notifications_list(context, team_id, non_expired, print_output=True):  # pylint: disable=inconsistent-return-statements
    """
    Function to list notifications policies

    Args:
        team_id: the id of the team
        non_expired: filters down notifications policies that are not closed and not acknowledged

    Returns:
        Table output listing the notifications policies for a team in the format of two columns: id, name, and enabled

    """
    if team_id:
        result = context.obj['opsgenie'].list_notification_policy(team_id)
    elif context.obj.get('teamid') and not team_id:
        result = context.obj['opsgenie'].list_notification_policy(context.obj.get('teamid'))
    else:
        raise click.UsageError(
            "No team id was found. Use --id or specify the team id in the config file.\n"
        )
    sortedlist = sorted(result['data'], key=itemgetter('name'))
    format_table = PrettyTable(['id', 'name', 'enabled'])
    for item in sortedlist:
        if non_expired:
            if item['enabled']:
                format_table.add_row([item['id'], item['name'], item['enabled']])
        else:
            format_table.add_row([item['id'], item['name'], item['enabled']])
    if print_output:
        print(format_table)
    else:
        return result


@bootstrapper.command()
@click.pass_context
def on_call(context):
    """
    Function to list the user on-call per team

    Returns:
        Table output listing the user on-call per team in the format of two columns: team, and EOD

    """
    result = context.obj['opsgenie'].get_users_on_call()
    table_eod = PrettyTable(['Team', 'EOD'])
    table_no_eod = PrettyTable(['Opsgenie teams without an EOD'])
    for item in result['data']:
        if item['onCallParticipants']:
            table_eod.add_row([item['_parent']['name'], item['onCallParticipants'][0]['name']])
        else:
            table_no_eod.add_row([item['_parent']['name']])
    print(table_no_eod)
    print(table_eod)


@bootstrapper.command(cls=DefaultHelp, name='override')
@click.option('--start_date', cls=MutuallyExclusiveOption, mutually_exclusive=["hours"],
              help='Example: 2019-03-15T14:34:09Z.')
@click.option('--end_date', cls=MutuallyExclusiveOption, mutually_exclusive=["hours"],
              help='Example: 2019-03-15T15:34:09Z')
@click.option('--team_name')
@click.option('--engineer', help='Name the username of the engineer who will be on call.')
@click.option('--hours', type=int, help='Amount of hours to set the override for.')
@click.pass_context
def override(context, team_name, engineer, hours, start_date, end_date):  # pylint: disable=too-many-arguments
    """
    Function to override the on-call schedule with another user

    Args:
        team_name: the name of the team
        engineer: the user who take the on-call duty
        hours: sets the start date to now and the end date to now + the amount of hours specified
        start_date: start date of the override
        end_date: end date of the override

    Returns:
        String output specifying which users will be on-call and the start- and end date on success, None otherwise

    Examples:
    $ opsgeniecli.py override --team_name <TEAMSCHEDULE> --engineer <ENGINEER> --hours <INTEGER>
    $ opsgeniecli.py override --team_name <TEAMSCHEDULE> --engineer <ENGINEER>
    --start_date 2019-03-15T14:34:09Z --end_date 2019-03-15T15:34:09Z

    """
    if hours:
        result = context.obj['opsgenie'].set_override_for_hours(team_name, engineer, hours)
        output_start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output_end_date = (datetime.now() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    elif start_date and end_date:
        result = context.obj['opsgenie'].set_override_scheduled(team_name, start_date, end_date, engineer)
        start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")
        output_start_date = start.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        output_end_date = end.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise click.UsageError(
            "Specify the amount of hours you want to override the schedule (using --hours), \
            or specify a schedule (using --start_date and --end_date)."
        )
    if result.status_code == 201:
        print(f"✓ - override set to {engineer} between {output_start_date} and {output_end_date}")
    else:
        print(result.text)


def main():
    """Main entry point of tool"""
    bootstrapper(obj={})  # pylint: disable=no-value-for-parameter, unexpected-keyword-arg


if __name__ == '__main__':
    main()
