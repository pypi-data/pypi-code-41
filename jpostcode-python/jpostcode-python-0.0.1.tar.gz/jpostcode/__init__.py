import csv
import os
import pathlib
from collections import Counter


csv_filepath = pathlib.Path(os.path.abspath(__file__)).parent / pathlib.Path('data') / pathlib.Path('KEN_ALL_ROME.CSV')

with open(csv_filepath, encoding='cp932') as csvfile:
    reader = csv.reader(csvfile)
    postcodes = list(reader)


def to_prefectures(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    filtered = filter(lambda x: x[0] == cleaned_postcode, postcodes)
    prefectures = [x[1] for x in filtered]
    return prefectures


def to_prefecture(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    filtered = filter(lambda x: x[0] == cleaned_postcode, postcodes)
    prefectures_counter = Counter([x[1] for x in filtered])
    return prefectures_counter.most_common(1)[0][0]


def to_cities(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    filtered = filter(lambda x: x[0] == cleaned_postcode, postcodes)
    cities = [x[2] for x in filtered]
    return cities


def to_city(postcode: str):
    cleaned_postcode = postcode.replace('-', '')
    filtered = filter(lambda x: x[0] == cleaned_postcode, postcodes)
    cities_counter = Counter([x[2] for x in filtered])
    return cities_counter.most_common(1)[0][0].replace('　', '')
