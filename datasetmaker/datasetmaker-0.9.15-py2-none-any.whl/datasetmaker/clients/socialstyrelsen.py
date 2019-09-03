import os
import shutil
import requests
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.entity import Country
from datasetmaker.indicator import concepts, sid_to_id
from pathlib import Path


# Desired result
# socialstyrelsen_
# patients_with_medicine,prescriptions
# patients--prescriptions--by--gender--region--


class SocialstyrelsenClient(Client):

    url = 'raw_data/socialstyrelsen/'

    def get(self, indicators=None, periods=None):

        atc_codes = pd.read_csv(self.url + "atc_codes.csv",  sep=';')


        #patients.to_csv(os.path.join(
         #   self.url, 'ddf--datapoints--patients--by--atc_code--gender--age_group.csv'), index=False)

        # self.data = {'laureates': df, 'prizes': prizes}
        return atc_codes

    def save(self, path, **kwargs):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        df, prizes = self.data['laureates'], self.data['prizes']

        nobel_concepts = concepts[(concepts.source == 'nobel') |
                                  (concepts.concept.isin(['country', 'gender']))]
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
        countries.to_csv(os.path.join(path, 'ddf--entities--country.csv'),
                         index=False)

        (prizes[['nobel_category']]
            .dropna()
            .drop_duplicates()
            .to_csv(os.path.join(path, 'ddf--entities--nobel_category.csv'),
                    index=False))

        dp_fname = ('ddf--datapoints--nobel_laureate--nobel_category--'
                    'nobel_motivation--by--year.csv')
        prizes.to_csv(os.path.join(path, dp_fname), index=False)

        meta = package.create_datapackage(path, **kwargs)
        dump_json(os.path.join(path, "datapackage.json"), meta)
