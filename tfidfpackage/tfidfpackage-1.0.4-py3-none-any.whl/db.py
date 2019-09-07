import sqlite3

import click


def clic():
    pass

    
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def drop_db():
    """Drop the existing data and create new tables."""
    drop_db()
    click.echo('Drop the database.')

if __name__== '__main__':
    clic()
    clic.add_Command(init_db)
    clic.add_Command(drop_db)
