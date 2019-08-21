import dsnparse
from datetime import date, datetime

from bs4 import BeautifulSoup
from pony.orm import Database, Required, db_session

db = Database()


class RepaymentHistory(db.Entity):
    date = Required(date)
    amount = Required(float)
    opening_balance = Required(float)
    principal = Required(float)
    interest = Required(float)
    fee = Required(float)
    closing_balance = Required(float)


class RepaymentSchedule(db.Entity):
    date = Required(date)
    amount = Required(float)
    opening_balance = Required(float)
    principal_repayment = Required(float)
    interest_repayment = Required(float)
    closing_balance = Required(float)


def connect_to_db(db_url):
    parsed_url = dsnparse.parse(db_url)

    db.bind(
        provider=parsed_url.scheme,
        host=parsed_url.host,
        port=parsed_url.port,
        user=parsed_url.username,
        passwd=parsed_url.password,
        db=parsed_url.database
    )
    db.generate_mapping(create_tables=True)


def parse_file(filename):
    with open(filename) as fp:
        soup = BeautifulSoup(fp, features="html.parser")
        tables = soup.find_all('table')
        return {
            'repayment_history': tables[2],
            'repayment_schedule': tables[3],
        }


@db_session
def add_repayment_history(table):
    rows = table.tbody.find_all('tr')

    for row in rows:
        data = row.find_all('td')

        if len(data) > 1:
            RepaymentHistory(
                date=datetime.strptime(data[0].string, '%d/%m/%Y'),
                amount=float(data[2].string[1:].replace(',', '')),
                opening_balance=float(data[3].string[1:].replace(',', '')),
                principal=float(data[4].string[1:].replace(',', '')),
                interest=float(data[5].string[1:].replace(',', '')),
                fee=float(data[6].string[1:].replace(',', '')),
                closing_balance=float(data[7].string[1:].replace(',', ''))
            )


@db_session
def add_repayment_schedule(table):
    rows = table.tbody.find_all('tr')

    for row in rows:
        data = row.find_all('td')

        if len(data) > 1:
            RepaymentSchedule(
                date=datetime.strptime(data[0].string, '%d/%m/%Y'),
                opening_balance=float(data[1].string[1:].replace(',', '')),
                amount=float(data[2].string[1:].replace(',', '')),
                interest_repayment=float(data[3].string[1:].replace(',', '')),
                principal_repayment=float(data[4].string[1:].replace(',', '')),
                closing_balance=float(data[5].string[1:].replace(',', ''))
            )
