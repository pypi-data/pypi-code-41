import click

from recodex.api import ApiClient
from recodex.decorators import pass_api_client


@click.group()
def cli():
    """
    Tools for groups manipulation
    """


@cli.command()
@click.argument("group_id")
@click.argument("user_id")
@pass_api_client
def join(api: ApiClient, group_id, user_id):
    """
    Add user as a member (student) of a group
    """

    api.group_add_student(group_id, user_id)


@cli.command()
@click.argument("group_id")
@click.argument("user_id")
@pass_api_client
def leave(api: ApiClient, group_id, user_id):
    """
    Remove user (student) from a group
    """

    api.group_remove_student(group_id, user_id)


@cli.command()
@click.argument("group_id")
@click.argument("exercise_id")
@pass_api_client
def attach(api: ApiClient, group_id, exercise_id):
    """
    Attach exercise to a group of residence
    """

    api.group_attach_exercise(group_id, exercise_id)


@cli.command()
@click.argument("group_id")
@click.argument("exercise_id")
@pass_api_client
def detach(api: ApiClient, group_id, exercise_id):
    """
    Detach exercise from a group of residence
    """

    api.group_detach_exercise(group_id, exercise_id)
