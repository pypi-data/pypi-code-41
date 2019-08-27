import click
from colorama import Fore, Style


def target_print(metrics, **kwargs):
    click.echo()
    for name, metric in metrics.items():
        click.echo('  {name}: '.format(name=name) + Fore.GREEN + str(metric['result']) + Style.RESET_ALL)
