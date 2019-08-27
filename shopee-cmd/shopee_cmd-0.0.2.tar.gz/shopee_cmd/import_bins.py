import click
import csv
import time
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopee_payment_module.settings")

from paylib.payment_channel_item import bank_manager
from paylib.payment_channel_item import db_manager


scheme_store = {
    'VISA': 1,
    'MASTERCARD': 2,
}

type_store = {
    'credit': 1,
    'debit': 2,
}


def create_bank(name, country, operator='SPM'):
    models = db_manager.get_banks(name=name, country=country)
    if not models:
        model = bank_manager.create_bank(name, country, operator)
    else:
        model = models[0]
    return model.bank_id


def create_bin(bin_number, bank_id, bin_type, brand, operator='SPM',
               extra_data='{"whitelisted_channel_ids":[3000502]}'):
    return bank_manager.create_bin_data(bin_number, bank_id, bin_type,
                                        brand, operator, extra_data)


@click.command()
@click.option('--not-dry-run', is_flag=True)
@click.argument('filename', type=click.Path(exists=True))
def run(not_dry_run, filename):
    """
    import_bins <tsv_file>

    tsv_file format

        bank    bin     scheme  type    country
        DBS BANK (HONG KONG), LTD       47607307        VISA    credit  HKG
        DBS BANK (HONG KONG), LTD       54181909        MASTERCARD      credit  HKG
        DBS BANK (HONG KONG), LTD       47607362        VISA    credit  HKG
        DBS BANK (HONG KONG), LTD       45395088        VISA    credit  HKG
        DBS BANK (HONG KONG), LTD       54080488        MASTERCARD      credit  HKG
        DBS BANK (HONG KONG), LTD       47607373        VISA    credit  HKG
        DBS BANK (HONG KONG), LTD       54181920        MASTERCARD      credit  HKG
        DBS BANK (HONG KONG), LTD       54181970        MASTERCARD      credit  HKG
        DBS BANK (HONG KONG), LTD       45183437        VISA    credit  HKG

    """
    fname = click.format_filename(filename)
    click.echo('filename is {}'.format(fname))

    keys = ['bank', 'bin', 'scheme', 'type', 'country']
    cnt = 0
    with open(fname) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            bank_name = row['bank']
            bin_number = row['bin'][:6]
            scheme = row['scheme']
            card_type = row['type']
            country = row['country']
            if scheme not in scheme_store:
                click.echo('unknown scheme: {}'.format(scheme))
                return
            if card_type not in type_store:
                click.echo('unknown type: {}'.format(card_type))
                return

            if not_dry_run:
                bank_id = create_bank(bank_name, country)
            click.echo('create_bank({}, {})'.format(bank_name, country))
            if not_dry_run:
                create_bin(bin_number, bank_id, type_store[card_type], scheme_store[scheme])
            click.echo('create_bin({}, {}, {}, {})'.format(bin_number, bank_id, type_store[card_type], scheme_store[scheme]))
            cnt += 1
            if cnt % 100 == 0:
                time.sleep(1)

    click.echo('DONE')

if __name__ == '__main__':
    run()
