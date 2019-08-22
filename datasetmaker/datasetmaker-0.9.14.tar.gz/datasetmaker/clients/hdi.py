import os
import shutil
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.entity import Country
from datasetmaker.indicator import concepts, sid_to_id


class HDI(Client):
    url = ('http://ec2-54-174-131-205.compute-1.amazonaws.com/'
           'API/hdro_api_all.json')

    def get(self, indicators=None, periods=None):
        df = pd.read_json(self.url)
        df['country'] = df.country_code.str.lower().map(Country.iso3_to_id())
        df = df.drop(['country_code', 'country_name', 'indicator_id'], axis=1)
        df.indicator_name = df.indicator_name.map(sid_to_id('hdi'))
        self.data = df
        return df

    def save(self, path, **kwargs):
        global concepts

        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        hdi_concepts = concepts[(concepts.source == 'hdi') |
                                (concepts.concept.isin(['country', 'year']))]
        hdi_concepts = hdi_concepts[['concept', 'concept_type', 'name', 'domain']]
        hdi_concepts.to_csv(os.path.join(
            path, 'ddf--concepts.csv'), index=False)

        for ind in self.data.indicator_name.unique():
            frame = self.data[self.data.indicator_name == ind]
            frame = frame.dropna(subset=['value'])
            frame = frame.rename(columns={'value': ind})
            frame = frame.drop('indicator_name', axis=1)
            frame.to_csv(os.path.join(
                path, f'ddf--datapoints--{ind}--by--country--year.csv'), index=False)

        (self.data.drop_duplicates(subset=['country'])[['country']]
            .to_csv(os.path.join(path, 'ddf--entities--country.csv'), index=False))

        meta = package.create_datapackage(path, **kwargs)
        dump_json(os.path.join(path, "datapackage.json"), meta)
