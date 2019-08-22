import csv
import json
import os
import requests

base_path = os.path.dirname(os.path.realpath(__file__))


def fetch_journals():
    url = 'https://www.ncbi.nlm.nih.gov/pmc/journals/?format=csv'
    response = requests.get(url)
    if response.status_code == 200:

        _atoj = {}
        _jtoa = {}
        dates = {}
        full = {}
        reader = csv.reader(response.text.split('\n'))
        header = False

        for row in reader:
            if not header:
                header = True
                continue
            if row:
                title, abbr, pissn, eissn, publisher, locator, latest, earliest, freeaccess, openaccess, participation, deposit, url = row
                _atoj[abbr.lower()] = title
                _jtoa[title.lower()] = abbr
                dates[abbr.lower()] = (earliest, latest)
                full[abbr.lower()] = row
        data = {'atoj': _atoj, 'jtoa': _jtoa, 'dates': dates, 'full': full}

        return data


def get_source(cache=False):
    """ return source dictionary of journals and abbreviations

    :param cache:
    :return:
    """
    if not cache:
        try:
            journals = fetch_journals()
        except requests.exceptions.HTTPError:
            pass
        except requests.exceptions.ProxyError:
            pass
        else:
            return journals
    with open(os.path.join(base_path, 'journals.json')) as f:
        journals = json.load(f)
    return journals


def get_abbreviations(cache=False):
    return get_source(cache)['atoj']


def get_journals(cache=False):
    return get_source(cache)['jtoa']


def get_dates(cache=False):
    return get_source(cache)['dates']


def atoj(abbrv, cache=False):
    data = get_abbreviations(cache)
    return data.get(abbrv.lower())


def jtoa(journal, cache=False):
    data = get_journals(cache)
    return data.get(journal.lower())


def atodates(abbrv, cache=False):
    data = get_dates(cache)
    return data.get(abbrv.lower())


if __name__ == '__main__':
    journals = fetch_journals()

    with open(os.path.join(base_path, 'journals.json'), 'w') as f:
        json.dump(journals, f)
