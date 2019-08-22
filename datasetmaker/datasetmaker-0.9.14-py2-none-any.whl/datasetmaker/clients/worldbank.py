import io
import os
import shutil
import requests
from ddf_utils import package
from ddf_utils.io import dump_json
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.entity import Country
from datasetmaker import indicator
from datasetmaker.indicator import concepts


class WorldBank(Client):
    @property
    def indicators(self):
        return concepts[(concepts.concept_type == 'measure') &
                        (concepts.source == 'worldbank')].concept.tolist()

    def _get_wbi(self, code, **kwargs):
        """Get a World Bank indicator for all countries."""

        url = f"http://api.worldbank.org/v2/country/all/indicator/{code}"
        kwargs.update({"format": "json", "page": 1})
        last_page = -1
        data = []

        while last_page != kwargs["page"]:
            resp = requests.get(url, kwargs)
            meta, page_data = resp.json()
            last_page = meta["pages"]
            kwargs["page"] = kwargs["page"] + 1
            if page_data is None:
                continue
            if last_page == 1:
                break
            data.extend(page_data)

        df = pd.DataFrame(data)

        # Expand all dict columns
        for col in df.columns.copy():
            try:
                expanded = pd.io.json.json_normalize(df[col], record_prefix=True)
                expanded.columns = [f"{col}.{x}" for x in expanded.columns]
                df = pd.concat([df, expanded], axis=1)
                df = df.drop(col, axis=1)
            except AttributeError:
                continue

        return df

    def get(self, indicators, periods=None):
        data = []
        if periods and len(periods) > 1:
            date = f'{periods[0]}:{periods[-1]}'
        elif periods:
            date = periods[0]
        else:
            date = None

        for ind in indicators:
            code = indicator.id_to_sid('worldbank')[ind]
            frame = self._get_wbi(code, date=date)
            if frame.empty:
                continue
            frame = frame.dropna(subset=['value'])
            data.append(frame)
        df = pd.concat(data, sort=True).reset_index(drop=True)
        df = df.drop(["decimal", "obs_status", "unit",
                      "country.id", "indicator.value"], axis=1)

        # Remove non-countries
        df = df[df.countryiso3code != '']

        # Standardize country identifiers
        iso3_to_id = Country.iso3_to_id()
        name_to_id = Country.name_to_id()
        df["country"] = df.countryiso3code.str.lower().map(iso3_to_id)
        df["country"] = df.country.fillna(df["country.value"].map(name_to_id))
        df = df.drop(["country.value", "countryiso3code"], axis=1)
        df = df[df.country.notnull()]
        df = df.rename(columns={"indicator.id": "indicator", "date": "year"})

        # Standardize indicator identifiers
        df.indicator = df.indicator.map(indicator.sid_to_id('worldbank'))

        self.data = df
        return df

    def save(self, path, **kwargs):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        self.data[["country"]].drop_duplicates().sort_values('country').to_csv(
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
            frame = self.data.query(f'indicator == "{ind}"')
            (frame
                .filter(['value', 'country', 'year'])
                .dropna(subset=['value'])
                .rename(columns={'value': ind})
                .to_csv(os.path.join(path, fname), index=False))

            concepts = concepts.append({
                'concept': ind,
                'concept_type': 'measure',
                'name': indicator.id_to_name(source='worldbank').get(ind)
            }, ignore_index=True)

        concepts.to_csv(os.path.join(path, "ddf--concepts.csv"), index=False)

        meta = package.create_datapackage(path, **kwargs)
        dump_json(os.path.join(path, "datapackage.json"), meta)

        return
