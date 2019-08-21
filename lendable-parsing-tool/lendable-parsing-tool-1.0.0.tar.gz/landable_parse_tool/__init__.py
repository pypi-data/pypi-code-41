import click

from landable_parse_tool.business import (
    connect_to_db, parse_file, add_repayment_history, add_repayment_schedule
)


@click.command()
@click.argument(
    'db_url',
    help='URL for the access to the database like '
         'mysql://<user>:<pass>@<host>:<port>/<db>'
)
@click.argument('filename', help='File to be imported')
def tool(db_url, filename):
    connect_to_db(db_url)
    parsed_tables = parse_file(filename)
    imported_repayment_history_amount = add_repayment_history(
        parsed_tables['repayment_history']
    )
    imported_repayment_schedule_amount = add_repayment_schedule(
        parsed_tables['repayment_schedule']
    )
    click.secho('Imported repayment histories: {}'.format(
            imported_repayment_history_amount
        ),
        fg='green'
    )
    click.secho('Imported repayment schedules: {}'.format(
            imported_repayment_schedule_amount,
            fg='green'
        )
    )
