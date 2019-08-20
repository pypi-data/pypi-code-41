import os

import click

from zabier import commands
from zabier.zabbix import configure


@click.group(invoke_without_command=True)
@click.option(
    '-H', '--host',
    required=False,
    type=str,
    default=os.environ.get('ZABBIX_HOST', ''))
@click.option(
    '-u', '--user',
    required=False,
    type=str,
    default=os.environ.get('ZABBIX_USER', ''))
@click.option(
    '-p', '--password',
    required=False,
    type=str,
    default=os.environ.get('ZABBIX_PASSWORD', ''))
@click.pass_context
def main(ctx: click.Context, host: str, user: str, password: str):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    else:
        configure(host, user, password)


@main.command(help='Apply the host group')
@click.option('-n', '--name', required=True, type=str)
@click.option('--dry-run', is_flag=True)
def hostgroup(name: str, dry_run: bool):
    commands.hostgroup(name, dry_run)


@main.command(help='Apply the action')
@click.option('-n', '--name', required=True, type=str)
@click.option('-f', '--file', required=True, type=str)
@click.option('--dry-run', is_flag=True)
def action(name: str, file: str, dry_run: bool):
    commands.action(name, file, dry_run)


@main.command(help='Apply the template')
@click.option('-n', '--name', required=True, type=str)
@click.option('-f', '--file', required=True, type=str)
@click.option('--dry-run', is_flag=True)
@click.option('--export', is_flag=True)
def template(name: str, file: str, dry_run: bool, export: bool):
    commands.template(name, file, dry_run, export)


@main.command(help='Apply the host')
@click.option('-n', '--name', required=True, type=str)
@click.option('-f', '--file', required=True, type=str)
@click.option('--dry-run', is_flag=True)
@click.option('--export', is_flag=True)
def host(name: str, file: str, dry_run: bool, export: bool):
    commands.host(name, file, dry_run, export)
