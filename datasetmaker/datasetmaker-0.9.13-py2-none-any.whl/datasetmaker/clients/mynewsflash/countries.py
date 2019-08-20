# import os
import pandas as pd
from .country_data import countries

pd.options.mode.chained_assignment = None


def remove_hyphens(text):
    return text.lower().replace('-', '').replace('–', '')


def map_all(x, mapping):
    return [mapping[i] for i in x]


def identify_countries(series):
    """Identifies countries mentioned in series.

    Parameters
    ----------
    series : pd.Series
        Series with text values.
    """
    # path = os.path.dirname(os.path.abspath(__file__))
    # path = os.path.join(path, 'countries.csv')
    # countries = pd.read_csv(path)
    global countries

    series = series.apply(remove_hyphens)

    countries = pd.DataFrame(countries)
    countries = countries.dropna(subset=['name_swe', 'adjective'])

    countries['adjective'] = countries['adjective'].fillna('')
    countries['name_swe_trimmed'] = countries['name_swe'].apply(remove_hyphens)
    countries = countries[countries.name_swe != 'Sverige']

    trimmed_name_map = countries[['name_swe', 'name_swe_trimmed']].copy()
    trimmed_name_map = trimmed_name_map.set_index('name_swe_trimmed')
    trimmed_name_map = trimmed_name_map['name_swe'].to_dict()

    pat_name = r'(\b' + r'|\b'.join(countries.name_swe_trimmed) + r'\b)s?\b'

    names_found = series.str.findall(pat_name)
    names_found = names_found.apply(map_all, args=(trimmed_name_map,))

    adj_name_map = countries[['name_swe', 'adjective']].copy()
    adj_name_map = adj_name_map.set_index('adjective')['name_swe'].to_dict()

    pat_adj = r'(\b' + r'|\b'.join(countries.adjective) + r'\b)s?'

    adjectives_found = series.str.findall(pat_adj)
    adjectives_found = adjectives_found.apply(map_all, args=(adj_name_map,))

    countries_found = (names_found + adjectives_found).apply(set)

    parent_name_map = countries[['name_swe', 'parent']].copy()
    parent_name_map = parent_name_map.set_index('name_swe')['parent'].to_dict()
    countries_found = countries_found.apply(map_all, args=(parent_name_map,))
    countries_found = countries_found.apply(set).apply(list).apply(sorted)

    return countries_found
