from invoke import task
from . import create


@task
def sidney(ctx, name):
    ''' all the jazz - creates everything.'''
    from bluemax.sa import tasks as database

    create.project(ctx, name, with_config=True)
    create.tests(ctx, name)
    create.docker(ctx, name)
    database.create(ctx, name)
