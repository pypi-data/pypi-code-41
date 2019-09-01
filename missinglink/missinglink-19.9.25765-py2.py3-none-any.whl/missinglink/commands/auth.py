# -*- coding: utf-8 -*-
import os

import click
from missinglink.core.config import default_missing_link_folder
from missinglink.core.context import init_context2
from terminaltables import PorcelainTable

from missinglink.commands.commons import print_as_json
from missinglink.core.api import ApiCaller

from missinglink.commands.http_session import create_http_session
from missinglink.commands.utilities.options import CommonOptions
from missinglink.commands.utilities.tables import dict_to_csv
from .commons import output_result


@click.group('auth', help='Authorization Commands.')
def auth_commands():
    pass


def _save_auth_config(ctx, refresh_token, id_token, access_token):
    ctx.obj.config.update_and_save({
        'token': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'id_token': id_token,
        }
    })


def _init_auth(ctx, webserver=True, save_config=True):
    from .commons import pixy_flow

    ctx.obj.local_web_server = webserver

    access_token, refresh_token, id_token = pixy_flow(ctx.obj)

    if save_config:
        _save_auth_config(ctx, refresh_token, id_token, access_token)

    return refresh_token, id_token, access_token


@auth_commands.command('init')
@click.pass_context
@click.option('--webserver/--disable-webserver', default=True, required=False, help='Enables or disables the webserver')
def init_auth(ctx, webserver):
    """Authenticates the CLI."""
    _init_auth(ctx, webserver)


@auth_commands.command('whoami')
@click.pass_context
def whoami(ctx):
    """Displays the info of the current user."""
    token_data = ctx.obj.config.token_data

    result = {
        'user_id': token_data.get('uid'),
        'name': token_data.get('name'),
        'email': token_data.get('email'),
    }
    json_format = ctx.obj.output_format == 'json'
    format_tables = not json_format

    if format_tables:
        fields = ['name', 'email', 'user_id']
        table_data = list(dict_to_csv(result, fields))

        click.echo(PorcelainTable(table_data).table)
    else:
        print_as_json(result)


@auth_commands.command('resource')
@CommonOptions.org_option()
@click.pass_context
def auth_resource(ctx, org):
    """Creates a service token for a specific resource."""
    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', '{org}/resource/authorise'.format(org=org))

    output_result(ctx, result, ['token'])

 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
