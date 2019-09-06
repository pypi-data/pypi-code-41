import io
import os
import shutil
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
import numpy as np
from datasetmaker.entity import Country
from datasetmaker import indicator
from datasetmaker.models import Client
from datasetmaker.utils import SDMXHandler

pd.options.mode.chained_assignment = None


class OECD(Client):
    def get(self, indicators, **kwargs):
        indicator_mapping = indicator.id_to_sid('oecd')
        indicators = [indicator_mapping[x] for x in indicators]
        sdmx = SDMXHandler('CSPCUBE', subject=indicators, **kwargs)
        df = pd.DataFrame(sdmx.data)

        # Standardize data
        df['country'] = df.Country.str.lower().map(
            Country.iso3_to_id())
        df['indicator'] = df.Subject.map(indicator.sid_to_id(source='oecd'))

        df = df.drop(['Country', 'Subject', 'Time Format', 'Unit multiplier',
                      'Unit', 'reference period'], axis=1, errors='ignore')
        df.columns = [x.lower() for x in df.columns]

        self.data = df
        return df

    def save(self, path, **kwargs):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        df_country = self.data[["country"]]
        df_country['name'] = df_country.country.map(
            Country.id_to_name())
        df_country.drop_duplicates().to_csv(
            os.path.join(path, "ddf--entities--country.csv"), index=False
        )

        concepts = (
            "concept,concept_type,name\n"
            "country,entity_domain,Country ID\n"
            "name,string,"
        )
        concepts = pd.read_csv(io.StringIO(concepts))

        for ind in self.data.indicator.unique():
            fname = f'ddf--datapoints--{ind}--by--country--year.csv'
            (self.data
                .query(f'indicator == "{ind}"')
                .filter(['value', 'country', 'year'])
                .rename(columns={'value': ind})
                .to_csv(os.path.join(path, fname), index=False))

            concepts = concepts.append({
                'concept': ind,
                'concept_type': 'measure',
                'name': indicator.id_to_name(source='oecd').get(ind)
            }, ignore_index=True)

        concepts.to_csv(os.path.join(path, "ddf--concepts.csv"), index=False)

        meta = package.create_datapackage(path, **kwargs)
        dump_json(os.path.join(path, "datapackage.json"), meta)

        return
