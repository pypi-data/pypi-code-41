import time
import click

from zec2 import get_aws_objects, get_instance_by_number, \
                 run_action, list_instances


@click.group()
@click.pass_context
@click.option('-p', '--aws_profile', help='AWS API profile')
def cli(context, aws_profile):
    ec2, vpcs = get_aws_objects(aws_profile)
    ec2.connection()
    context.obj = {
        'aws_profile': aws_profile,
        'objects': {
            'ec2': ec2,
            'vpcs': vpcs
        }
    }


@cli.command()
@click.pass_context
@click.option('-f/-no-f', default=False, help='Run ls forever')
def ls(context, f):
    if f:
        while True:
            click.clear()
            list_instances(**context.obj.get('objects'))
            time.sleep(2)
    else:
        list_instances(**context.obj.get('objects'))


@cli.command()
@click.pass_context
@click.argument('number')
@click.option('-u', '--user', help='SSH user')
@click.option('-i', '--key_path', help='AWS Key Pair')
def ssh(context, number, user, key_path):
    instance = get_instance_by_number(number, **context.obj.get('objects'))
    click.echo(instance.ssh_command(user, key_path))


@cli.command()
@click.pass_context
@click.argument('number')
def start(context, number):
    run_action(number, 'start', **context.obj.get('objects'))


@cli.command()
@click.pass_context
@click.argument('number')
def stop(context, number):
    run_action(number, 'stop', **context.obj.get('objects'))


@cli.command()
@click.pass_context
@click.argument('number')
def restart(context, number):
    run_action(number, 'restart', **context.obj.get('objects'))


@cli.command()
@click.pass_context
@click.argument('number')
def terminate(context, number):
    run_action(number, 'terminate', **context.obj.get('objects'))
