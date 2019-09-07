import click

from . import __version__, Uninstaller


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('v' + __version__)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help="Show version and exit.")
def cli():
    pass


@cli.command(help="Remove the version of .Net Core.")
@click.option('--no-input', is_flag=True, help='Deletes the files without asking the user')
@click.option('--sdk', help='Deletes the files without asking the user')
@click.option('--runtime', help='Deletes the files without asking the user')
def remove(no_input, sdk, runtime):
    if not no_input:
        click.confirm('Do you want to continue?', abort=True)

    if sdk:
        Uninstaller().delete_sdk(sdk)

    if runtime:
        Uninstaller().delete_runtime(runtime)

    if sdk is None and runtime is None:
        click.echo("No SDK or runtime version provided.")


@cli.command('list', help="List all the version of .Net Core installed.")
def list_dotnet():
    Uninstaller().list_dotnet()
