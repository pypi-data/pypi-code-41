import os
import shutil
import lxml
import requests
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.entity import Country
from datasetmaker.indicator import concepts


class UNSC(Client):
    url = 'https://scsanctions.un.org/resources/xml/en/consolidated.xml'

    def get(self, indicators=None, periods=None):
        r = requests.get(self.url)
        etree = lxml.etree.fromstring(bytes(r.text, encoding='utf8'))
        individuals = self._xml_to_frame(etree, 'INDIVIDUALS', 'INDIVIDUAL')
        entities = self._xml_to_frame(etree, 'ENTITIES', 'ENTITY')

        # These fields are all empty or irrelevant to us
        drop_cols_individuals = [
            'DESIGNATION',
            'INDIVIDUAL_ADDRESS',
            'INDIVIDUAL_ALIAS',
            'INDIVIDUAL_DATE_OF_BIRTH',
            'INDIVIDUAL_DOCUMENT',
            'INDIVIDUAL_PLACE_OF_BIRTH',
            'LAST_DAY_UPDATED',
            'LIST_TYPE',
            'NATIONALITY',
            'SORT_KEY',
            'SORT_KEY_LAST_MOD',
            'TITLE'
        ]

        individuals = individuals.drop(drop_cols_individuals, axis=1)

        drop_cols_entities = [
            'ENTITY_ADDRESS',
            'ENTITY_ALIAS',
            'LAST_DAY_UPDATED',
            'LIST_TYPE',
            'SORT_KEY',
            'SORT_KEY_LAST_MOD'
        ]

        entities = entities.drop(drop_cols_entities, axis=1)

        individuals.columns = [
            f'unsc_{x.lower()}' for x in individuals.columns]
        individuals = individuals.rename(columns={
            'unsc_gender': 'gender',
            'unsc_dataid': 'unsc_sanctioned_individual'})
        entities.columns = [f'unsc_{x.lower()}' for x in entities.columns]
        entities = entities.rename(
            columns={'unsc_dataid': 'unsc_sanctioned_entity'})

        individuals.unsc_submitted_by = individuals.unsc_submitted_by.map(
            Country.name_to_id()
        )

        df = {'individuals': individuals, 'entities': entities}

        self.data = df
        return df

    def _xml_to_frame(self, etree, rootname, nodename):
        nodes = etree.find(rootname).findall(nodename)
        data = []

        for node in nodes:
            entry = {}
            for prop in node.getchildren():
                entry[prop.tag] = prop.text
            data.append(entry)

        return pd.DataFrame(data)

    def save(self, path, **kwargs):
        global concepts

        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        unsc_concepts = concepts[(concepts.source == 'unsc') |
                                 (concepts.concept.isin(['country', 'gender']))]
        unsc_concepts = unsc_concepts[['concept', 'concept_type', 'name', 'domain']]
        unsc_concepts.to_csv(os.path.join(
            path, 'ddf--concepts.csv'), index=False)

        self.data['individuals'].to_csv(os.path.join(
            path, 'ddf--entities--unsc_sanctioned_individual.csv'), index=False)

        self.data['entities'].to_csv(os.path.join(
            path, 'ddf--entities--unsc_sanctioned_entity.csv'), index=False)

        (self.data['individuals'][['unsc_submitted_by']]
            .dropna()
            .drop_duplicates()
            .rename(columns={'unsc_submitted_by': 'country'})
            .to_csv(
                os.path.join(path, 'ddf--entities--country.csv'), index=False))
        
        (self.data['individuals'][['gender']]
            .dropna()
            .assign(gender=lambda x: x.gender.str.lower())
            .drop_duplicates()
            .to_csv(
                os.path.join(path, 'ddf--entities--gender.csv'), index=False))

        meta = package.create_datapackage(path, **kwargs)
        dump_json(os.path.join(path, "datapackage.json"), meta)

        return
