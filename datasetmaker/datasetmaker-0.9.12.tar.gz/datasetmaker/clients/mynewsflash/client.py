import io
import os
import pathlib
import shutil
import datetime
import pytz
import pandas as pd
import requests
from ddf_utils import package
from ddf_utils.io import dump_json
from datasetmaker.models import Client
from .corpus import ArticleDropper
from .pipeline import create_pipeline
from .utils import stretch


def remove_hyphens(text):
    return text.lower().replace('-', '').replace('–', '')


def map_all(x, mapping):
    return [mapping[i] for i in x]


class MyNewsFlashClient(Client):
    domains = [
        'dn.se',
        'svt.se',
        'aftonbladet.se',
        'expressen.se',
        'sydsvenskan.se',
        'gp.se',
        'svd.se',
        'sr.se']
    API_KEY = os.environ.get('MYNEWSFLASH_TOKEN')
    URL = 'https://api.mynewsflash.se/v1/search.json'

    def _fetch_hour(self, hour):
        """
        Fetches all results for a given hour.

        Parameters
        ----------
        hour : datetime.datetime
            Hour to search.
        """
        params = {
            'key': self.API_KEY,
            'require_domains': ','.join(self.domains),
            'unique': 'true',
            'indexed_from': hour.isoformat(),
            'indexed_to': (hour+datetime.timedelta(hours=1)).isoformat(),
            'q': '"*"',
            'limit': 500}

        r = requests.get(self.URL, params=params)
        print(r.status_code)
        return r.json().get('result')

    def _fetch_period(self, start, end):
        """
        Fetches all results between start and end.

        Parameters
        ----------
        start : datetime.datetime
            Start of time period.
        end : datetime.datetime
            End of time period.
        """
        results = list()
        for hour in range(int((end - start).total_seconds() / 60 / 60)):
            offset = datetime.timedelta(hours=hour)
            results.extend(self._fetch_hour(start + offset))
        return results

    def _read_latest_timestamp(self):
        """
        Look up datetime of latest retrieved article.
        """
        path = pathlib.Path(self._raw_data_path)
        fnames = sorted([x for x in path.glob('*.csv')])
        latest_month_path = fnames[-1]
        frame = pd.read_csv(latest_month_path)
        frame.indexed = pd.to_datetime(frame.indexed)
        return frame.indexed.sort_values().iloc[-1]

    def _sync_raw_data(self, df, path):
        """
        Download and write missing articles to disc.

        Parameters
        ----------
        df : pd.DataFrame
            Dataframe with new articles.
        path : pathlib.Path
            Path to raw data directory.
        """
        df.indexed = pd.to_datetime(df.indexed)
        df['label'] = df.indexed.dt.year.astype(str)
        df.label = df.label + '-'
        df.label = df.label + (df.indexed.dt.month.astype(str).str.zfill(2))
        for label in df.label.unique():
            fname = path / f'{label}.csv'
            if fname.exists():
                month = pd.read_csv(fname)
                month.indexed = pd.to_datetime(month.indexed)
                month = pd.concat([month, df[df.label == label]].copy(),
                                  sort=True)
            else:
                month = df[df.label == label].copy()
            month = month.sort_values(['indexed', 'headline'])
            month = month.drop(['country',
                                'image',
                                'language',
                                'links',
                                'reference',
                                'label'], axis=1)

            month.to_csv(fname, index=False)

    def _filter_foreign_news(self, df):
        df['countries'] = self._identify_countries(df.headline + ' ' + df.lead)
        df.countries = df.countries.apply(lambda x: ','.join(x))
        df = df[(df.countries.notnull()) & (df.countries != '')]

        return df

    def _identify_countries(self, series):
        """Identifies countries mentioned in series.

        Parameters
        ----------
        series : pd.Series
            Series with text values.
        """
        from .country_data import countries

        series = series.apply(remove_hyphens)

        countries = pd.DataFrame(countries)
        countries = countries.dropna(subset=['name_swe', 'adjective'])

        countries['adjective'] = countries['adjective'].fillna('')
        countries['name_swe_trimmed'] = countries['name_swe'].apply(
            remove_hyphens)
        countries = countries[countries.name_swe != 'Sverige']

        trimmed_name_map = countries[['name_swe', 'name_swe_trimmed']].copy()
        trimmed_name_map = trimmed_name_map.set_index('name_swe_trimmed')
        trimmed_name_map = trimmed_name_map['name_swe'].to_dict()

        pat_name = r'(\b' + r'|\b'.join(countries.name_swe_trimmed) + r'\b)s?\b'

        names_found = series.str.findall(pat_name)
        names_found = names_found.apply(map_all, args=(trimmed_name_map,))

        adj_name_map = countries[['name_swe', 'adjective']].copy()
        adj_name_map = adj_name_map.set_index(
            'adjective')['name_swe'].to_dict()

        pat_adj = r'(\b' + r'|\b'.join(countries.adjective) + r'\b)s?'

        adjectives_found = series.str.findall(pat_adj)
        adjectives_found = adjectives_found.apply(
            map_all, args=(adj_name_map,))

        countries_found = (names_found + adjectives_found).apply(set)

        parent_name_map = countries[['name_swe', 'parent']].copy()
        parent_name_map = parent_name_map.set_index('name_swe')[
            'parent'].to_dict()
        countries_found = countries_found.apply(
            map_all, args=(parent_name_map,))
        countries_found = countries_found.apply(set).apply(list).apply(sorted)

        return countries_found

    def _predict_topics(self, df):
        classes = ['accidents', 'crime', 'culture', 'economy',
                   'nature', 'politics', 'protests', 'science', 'sports']
        pipe = create_pipeline(train=False)
        predictions = pipe.predict(df)
        label_matrix = pd.DataFrame(predictions,
                                    columns=[f'is_{x}' for x in classes])
        return pd.concat([df.reset_index(drop=True), label_matrix], axis=1)

    def get(self, raw_data_path):
        self._raw_data_path = pathlib.Path(raw_data_path)
        start_time = self._read_latest_timestamp()
        end_time = datetime.datetime.now(tz=pytz.timezone('UTC'))
        new_data = self._fetch_period(start_time, end_time)
        new_df = pd.DataFrame(new_data)
        if new_df.empty:
            return

        self._sync_raw_data(new_df, self._raw_data_path)

        dropper = ArticleDropper(drop_duplicates=False)

        foreign_data = []
        for monthly_file in list(self._raw_data_path.glob('*.csv')):
            df = pd.read_csv(monthly_file)
            df = dropper.transform(df)
            df = df.pipe(self._filter_foreign_news)
            foreign_data.append(df)

        df = pd.concat(foreign_data, sort=True)
        df = df.pipe(self._predict_topics)
        df = df.pipe(stretch, 'countries')
        df = df.rename({'countries': 'country'})

        self.data = df
        return df

    def save(self, path, **kwargs):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

        concepts = (
            "concept,concept_type,name\n"
            "country,entity_domain,Country ID\n"
            "article_count,measure,Number of articles\n"
            "name,string,"
        )
        concepts = pd.read_csv(io.StringIO(concepts))
        concepts.to_csv(os.path.join(path, 'ddf--concepts.csv'), index=False)

        (self.data
            .groupby('country')
            .size()
            .to_frame(name='article_count')
            .reset_index()
            .sort_values('country')
            .to_csv(os.path.join(path,
                                 'ddf--entities--article_count--by--country.csv'), index=False))

        meta = package.create_datapackage(path, **kwargs)
        dump_json(os.path.join(path, "datapackage.json"), meta)
