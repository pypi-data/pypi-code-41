import csv
import os
import pathlib
from collections import Counter
from itertools import groupby


csv_filepath = pathlib.Path(os.path.abspath(__file__)).parent / pathlib.Path('data') / pathlib.Path('KEN_ALL_ROME.CSV')

with open(csv_filepath, encoding='cp932') as csvfile:
    reader = csv.reader(csvfile)
    postcodes = list(reader)

postcode_dic = {x[0]: [(row[1], row[2]) for row in x[1]] for x in groupby(postcodes, lambda postcode: postcode[0])}


def to_prefectures(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    filtered = filter(lambda x: x[0] == cleaned_postcode, postcodes)
    prefectures = [x[1] for x in filtered]
    return prefectures


def to_prefecture(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    data = postcode_dic.get(cleaned_postcode, None)
    if not data:
        return None

    prefectures_counter = Counter([x[0] for x in data])
    try:
        most_common = prefectures_counter.most_common(1)
        return most_common[0][0]
    except IndexError:
        return None


def to_cities(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    filtered = filter(lambda x: x[0] == cleaned_postcode, postcodes)
    cities = [x[2] for x in filtered]
    return cities


def to_city(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    data = postcode_dic.get(cleaned_postcode, None)
    if not data:
        return None

    cities_counter = Counter([x[1] for x in data])
    try:
        most_common = cities_counter.most_common(1)
        return most_common[0][0].replace('　', '')
    except IndexError:
        return None
