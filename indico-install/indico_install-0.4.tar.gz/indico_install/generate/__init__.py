from indico_install.generate.update import update
import click


@click.group("generate")
def generate():
    """Scale and configure cluster from dump"""
    pass


generate.add_command(update)
