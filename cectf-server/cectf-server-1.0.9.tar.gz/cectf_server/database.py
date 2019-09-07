

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore, utils


db = SQLAlchemy()


def init_db():
    db.create_all()


def reset_db():
    db.drop_all()
    db.create_all()


def init_test_db():
    from .models import Role, User, RolesUsers, Challenge, Solve

    admin_role = Role(
        name="admin",
        description="Site admin")
    contestant_role = Role(
        name="contestant",
        description="CTF contestant")

    db.session.add(admin_role)
    db.session.add(contestant_role)
    db.session.commit()

    a_user = User(
        username="a",
        email="a@chiquito.com",
        password=utils.hash_password("b"),
        active=True)
    abc_user = User(
        username="abc",
        email="abc@chiquito.com",
        password=utils.hash_password("123"),
        active=True)

    db.session.add(a_user)
    db.session.add(abc_user)
    db.session.commit()

    a_contestant = RolesUsers(
        user_id=a_user.id,
        role_id=contestant_role.id)

    abc_admin = RolesUsers(
        user_id=abc_user.id,
        role_id=admin_role.id)

    db.session.add(a_contestant)
    db.session.add(abc_admin)
    db.session.commit()

    first_challenge = Challenge(
        title="The First Challenge",
        category="crypto",
        body="Just think really hard!",
        hint="CTF{l0l}",
        solution="CTF{l0l}")
    second_challenge = Challenge(
        title="The Second Challenge",
        category="reversing",
        body="Just think really harder!",
        hint="no cheatin",
        solution="CTF{1337}")

    db.session.add(first_challenge)
    db.session.add(second_challenge)
    db.session.commit()

    a_first = Solve(
        user_id=a_user.id,
        challenge_id=first_challenge.id,
        solved=False,
        hinted=False,
    )
    a_second = Solve(
        user_id=a_user.id,
        challenge_id=second_challenge.id,
        solved=False,
        hinted=False,
    )
    abc_first = Solve(
        user_id=abc_user.id,
        challenge_id=first_challenge.id,
        solved=False,
        hinted=False,
    )
    abc_second = Solve(
        user_id=abc_user.id,
        challenge_id=second_challenge.id,
        solved=False,
        hinted=False,
    )
    db.session.add(a_first)
    db.session.add(a_second)
    db.session.add(abc_first)
    db.session.add(abc_second)
    db.session.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('reset-db')
@with_appcontext
def reset_db_command():
    """Delete all existing data and create new tables."""
    reset_db()
    click.echo('Reset the database.')


@click.command('init-test-db')
@with_appcontext
def init_test_db_command():
    """Put test data into the database"""
    init_test_db()
    click.echo('Inserted test data')


def init_app(app):
    global user_datastore

    db.init_app(app)
    db.app = app

    from .models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(init_test_db_command)
