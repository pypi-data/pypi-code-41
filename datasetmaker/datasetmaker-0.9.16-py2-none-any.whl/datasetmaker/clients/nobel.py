import os
import shutil
import requests
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.entity import Country
from datasetmaker.indicator import concepts, sid_to_id


class NobelClient(Client):
    url = 'http://api.nobelprize.org/v1/laureate.json'

    def get(self, indicators=None, periods=None):
        r = requests.get(self.url)
        data = r.json()
        df = pd.DataFrame(data['laureates'])

        prizes = pd.io.json.json_normalize(data['laureates'],
                                           record_path='prizes',
                                           meta=['id'])
        prizes = prizes.drop(['affiliations', 'share', 'overallMotivation'],
                             axis=1, errors='ignore')
        prizes.columns = prizes.columns.map(sid_to_id('nobel'))
        prizes = prizes.dropna(subset=['nobel_category'])

        df.columns = df.columns.map(sid_to_id('nobel'))
        df = df[df.columns.dropna()]

        df.nobel_born_country = self._clean_country_col(df.nobel_born_country)
        df.nobel_died_country = self._clean_country_col(df.nobel_died_country)

        self.data = {'laureates': df, 'prizes': prizes}
        return df

    def _clean_country_col(self, series):
        return (series
                .str.replace('\([\w\' ]+\)', '')
                .str.replace('Scotland', 'United Kingdom')
                .str.replace('Northern Ireland', 'United Kingdom')
                .str.replace('W&uuml;rttemberg', 'Germany')
                .str.replace('German-occupied Poland', 'Poland')
                .str.strip()
                .str.lower()
                .map(Country.name_to_id()))

    def _save_instances(self, path):
        df = self.data['prizes']
        df = df.drop('nobel_laureate', axis=1)
        df = df.drop_duplicates()
        df['nobel_instance'] = df.nobel_category + '_' + df.year
        df.to_csv(path, index=False)

    def _save_prizes(self, path):
        df = self.data['prizes'].merge(self.data['laureates'],
                                       on='nobel_laureate')
        df['nobel_instance'] = df.nobel_category + '_' + df.year
        df['nobel_prize'] = df.nobel_category + '_' + df.year + '_' + df.nobel_laureate
        df = df[['nobel_prize', 'nobel_instance', 'nobel_laureate']]
        df.to_csv(path, index=False)

    def save(self, path, **kwargs):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        df, prizes = self.data['laureates'], self.data['prizes']

        nobel_concepts = concepts[(concepts.source == 'nobel') |
                                  (concepts.concept.isin(['country', 'gender', 'name']))]
        nobel_concepts = nobel_concepts[[
            'concept', 'concept_type', 'name', 'domain']]
        nobel_concepts.to_csv(os.path.join(
            path, 'ddf--concepts.csv'), index=False)

        df.to_csv(os.path.join(
            path, 'ddf--entities--nobel_laureate.csv'), index=False)

        countries = pd.concat([df.nobel_born_country,
                               df.nobel_died_country])
        countries = countries.dropna().drop_duplicates()
        countries = countries.to_frame(name='country')
        countries['name'] = countries.country.map(Country.id_to_name())
        countries.to_csv(os.path.join(path, 'ddf--entities--country.csv'),
                         index=False)

        self._save_instances(path=os.path.join(path, 'ddf--entities--nobel_instance.csv'))
        self._save_prizes(path=os.path.join(path, 'ddf--entities--nobel_prize.csv'))

        categories = (prizes[['nobel_category']]
            .dropna()
            .drop_duplicates())

        categories['name'] = categories.nobel_category.str.title()
        
        categories.to_csv(os.path.join(path, 'ddf--entities--nobel_category.csv'),
                    index=False)

        meta = package.create_datapackage(path, **kwargs)
        dump_json(os.path.join(path, "datapackage.json"), meta)
