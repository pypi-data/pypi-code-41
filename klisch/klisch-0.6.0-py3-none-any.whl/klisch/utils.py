import click


def color_print(string, color=None, background=None):
    click.secho(string, fg=color, bg=background)
